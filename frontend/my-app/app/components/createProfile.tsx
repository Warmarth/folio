"use client";

import { useState } from "react";

type CreateEditComponentProps = {
  onClick: () => void;
  onSubmit: (e: React.FormEvent<HTMLFormElement>) => void;

  name: string;
  setName: (value: string) => void;

  bio: string;
  setBio: (value: string) => void;

  image: File | null;
  setImage: (file: File | null) => void;

  creating: boolean;

  mode?: "create" | "edit";
};

export default function CreateEditComponent({
  onClick,
  onSubmit,
  name,
  setName,
  bio,
  setBio,
  image,
  setImage,
  creating,
  mode = "create",
}: CreateEditComponentProps) {
  const [imagePreview, setImagePreview] = useState<string | null>(null);

  const isEdit = mode === "edit";

  function handleImageChange(
    e: React.ChangeEvent<HTMLInputElement>
  ) {
    const file = e.target.files?.[0] || null;

    setImage(file);

    if (file) {
      setImagePreview(URL.createObjectURL(file));
    } else {
      setImagePreview(null);
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 px-4 backdrop-blur-sm">
      <div className="relative w-full max-w-md rounded-lg bg-[#f3efe3] p-7 text-[#1f1b16] shadow-2xl">

        {/* Close */}
        <button
          type="button"
          onClick={onClick}
          className="absolute right-5 top-5 flex h-8 w-8 items-center justify-center rounded-full text-black/40 transition hover:bg-black/5 hover:text-black"
        >
          ✕
        </button>

        {/* Header */}
        <div className="mb-7">
          <p className="font-mono text-[10px] uppercase tracking-[0.2em] text-[#3e7c74]">
            Your Folio
          </p>

          <h2 className="mt-2 font-serif text-2xl font-medium">
            {isEdit ? "Edit your profile" : "Create your profile"}
          </h2>

          <p className="mt-2 text-sm leading-relaxed text-black/50">
            {isEdit
              ? "Update your profile information."
              : "Tell people a little about yourself and what you are learning or building."}
          </p>
        </div>

        {/* Form */}
        <form onSubmit={onSubmit} className="space-y-5">

          {/* Name */}
          <div>
            <label className="mb-2 block font-mono text-[10px] uppercase tracking-wider text-black/50">
              Name
            </label>

            <input
              type="text"
              placeholder="e.g. Ibeaka Godson"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              className="w-full rounded-sm border border-black/10 bg-[#ebe6d7] px-4 py-3 text-sm outline-none transition placeholder:text-black/30 focus:border-[#3e7c74] focus:ring-1 focus:ring-[#3e7c74]"
            />
          </div>

          {/* Bio */}
          <div>
            <label className="mb-2 block font-mono text-[10px] uppercase tracking-wider text-black/50">
              About you
            </label>

            <textarea
              placeholder="Tell us about yourself, your skills, or what you're currently learning..."
              value={bio}
              onChange={(e) => setBio(e.target.value)}
              rows={4}
              className="w-full resize-none rounded-sm border border-black/10 bg-[#ebe6d7] px-4 py-3 text-sm leading-relaxed outline-none transition placeholder:text-black/30 focus:border-[#3e7c74] focus:ring-1 focus:ring-[#3e7c74]"
            />
          </div>

          {/* Image */}
          <div>
            <label className="mb-2 block font-mono text-[10px] uppercase tracking-wider text-black/50">
              Profile photo
            </label>

            <label className="flex cursor-pointer items-center gap-4 rounded-sm border border-dashed border-black/20 bg-[#ebe6d7] p-4 transition hover:border-[#3e7c74]">

              {/* Preview */}
              <div className="flex h-14 w-14 shrink-0 items-center justify-center overflow-hidden rounded-full bg-[#dcd7c8] font-serif text-xl text-black/30">
                {imagePreview ? (
                  <img
                    src={imagePreview}
                    alt="Profile preview"
                    className="h-full w-full object-cover"
                  />
                ) : (
                  "+"
                )}
              </div>

              <div>
                <p className="font-mono text-[11px] uppercase tracking-wider text-black/70">
                  {image ? "Change photo" : "Choose a photo"}
                </p>

                <p className="mt-1 text-xs text-black/40">
                  PNG, JPG or WebP · Max 2MB
                </p>
              </div>

              <input
                type="file"
                accept="image/png,image/jpeg,image/webp,image/gif"
                className="hidden"
                onChange={handleImageChange}
              />
            </label>
          </div>

          {/* Buttons */}
          <div className="flex gap-3 pt-2">

            <button
              type="button"
              onClick={onClick}
              className="flex-1 rounded-sm border border-black/10 py-3 font-mono text-[10px] uppercase tracking-wider text-black/50 transition hover:border-black/20 hover:text-black"
            >
              Cancel
            </button>

            <button
              type="submit"
              disabled={creating}
              className="flex-1 rounded-sm bg-[#1f1b16] py-3 font-mono text-[10px] uppercase tracking-wider text-[#f3efe3] transition hover:bg-[#33291d] disabled:cursor-not-allowed disabled:opacity-50"
            >
              {creating
                ? isEdit
                  ? "Saving..."
                  : "Creating..."
                : isEdit
                ? "Save changes"
                : "Create profile"}
            </button>

          </div>
        </form>
      </div>
    </div>
  );
}