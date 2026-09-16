"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";

const API_URL = process.env.NEXT_PUBLIC_API_URL;

export default function MentorRegisterPage() {
  const router = useRouter();

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [bio, setBio] = useState("");
  const [expertise, setExpertise] = useState("");
  const [image, setImage] = useState<File | null>(null);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  async function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
     const token = localStorage.getItem("access_token");

    if (!token) {
      console.log("No access token");
      return;
    }

    setError("");
    setSuccess("");

    if (!name.trim()) {
      setError("Please enter your name.");
      return;
    }

    if (!email.trim()) {
      setError("Please enter your email.");
      return;
    }

    if (!bio.trim()) {
      setError("Please enter a bio.");
      return;
    }
    setLoading(true);

    try {
      let imageUrl: string | undefined;

      // step 1: if an image was picked, upload it first and get back its URL
      if (image) {
        const imageFormData = new FormData();
        imageFormData.append("image", image);

        const uploadResponse = await fetch(`${API_URL}/api/upload_image`, {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
          },
          body: imageFormData,
        });

        const uploadData = await uploadResponse.json();

        if (!uploadResponse.ok) {
          throw new Error(uploadData.error || "Failed to upload image");
        }

        imageUrl = uploadData.image_url;
      }

      // step 2: create the mentor profile with the resulting image_url (if any)
      const response = await fetch(
        `${API_URL}/api/mentors_create_profile`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            name: name.trim(),
            bio: bio.trim(),
            expertise: expertise.trim(),
            image_url:imageUrl
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        setError(
          data.error || data.message || "Failed to create mentor account."
        );
        return;
      }

      setSuccess("Mentor account created successfully.");

      // If your backend returns a token:
      setTimeout(() => {
        router.push("/mentor/dashboard");
      }, 1000);
    } catch (error) {
      console.error("Mentor registration error:", error);
      setError("Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-[#f3efe3] flex items-center justify-center px-6 py-12">
      <div className="w-full max-w-xl bg-white border border-black/10 rounded-lg p-8">
        <div className="mb-8">
          <h1 className="text-3xl font-serif text-[#1f1b16]">
            Become a mentor
          </h1>

          <p className="mt-2 text-sm text-black/50">
            Create your Folio mentor profile and help learners
            develop practical skills.
          </p>
        </div>

        {error && (
          <div className="mb-5 rounded-lg bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-600">
            {error}
          </div>
        )}

        {success && (
          <div className="mb-5 rounded-lg bg-green-50 border border-green-200 px-4 py-3 text-sm text-green-700">
            {success}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-5">
          {/* Name */}
          <div>
            <label className="block text-sm font-medium mb-2">
              Full name
            </label>

            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="John Doe"
              className="w-full border border-black/10 rounded-lg px-4 py-3 outline-none focus:border-black/40"
            />
          </div>

          {/* Email */}
          <div>
            <label className="block text-sm font-medium mb-2">
              Email
            </label>

            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="john@example.com"
              className="w-full border border-black/10 rounded-lg px-4 py-3 outline-none focus:border-black/40"
            />
          </div>

          {/* Bio */}
          <div>
            <label className="block text-sm font-medium mb-2">
              About you
            </label>

            <textarea
              value={bio}
              onChange={(e) => setBio(e.target.value)}
              placeholder="Tell learners about your experience..."
              rows={5}
              maxLength={500}
              className="w-full border border-black/10 rounded-lg px-4 py-3 outline-none focus:border-black/40 resize-y"
            />

            <p className="mt-1 text-xs text-black/40">
              {bio.length}/500
            </p>
          </div>

          {/* Expertise */}
          <div>
            <label className="block text-sm font-medium mb-2">
              Expertise
            </label>

            <input
              type="text"
              value={expertise}
              onChange={(e) => setExpertise(e.target.value)}
              placeholder="Python, AI, Backend Development"
              maxLength={500}
              className="w-full border border-black/10 rounded-lg px-4 py-3 outline-none focus:border-black/40"
            />
          </div>

          {/* Image */}
          <div>
            <label className="block text-sm font-medium mb-2">
              Profile image
            </label>

            <input
              type="file"
              accept="image/*"
              onChange={(e) =>
                setImage(e.target.files?.[0] || null)
              }
              className="w-full text-sm"
            />
          </div>

          {/* Submit */}
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-[#1f1b16] text-[#f3efe3] px-5 py-3 rounded-lg disabled:opacity-50"
          >
            {loading
              ? "Creating mentor account..."
              : "Create Mentor Account"}
          </button>
        </form>
      </div>
    </main>
  );
}