"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import CreateEditComponent from "../components/createProfile";
import Link from "next/link";

type UserProfile = {
  name?: string;
  email?: string;
  bio?: string;
  image_url?: string;
  created_at?: string;
  item_count?: number;
  view_count?: number;
};

type ProfileMode = "create" | "edit";
const API_URL = process.env.NEXT_PUBLIC_API_URL;

export default function DashboardPage() {
  const router = useRouter();

  const [user, setUser] = useState<UserProfile | null>(null);
  const [showProfileForm, setShowProfileForm] = useState(false);
  const [showProfileEditForm, setShowProfileEditForm] = useState(false);
  const [name, setName] = useState("");
  const [bio, setBio] = useState("");
  const [image, setImage] = useState<File | null>(null);
  const [creating, setCreating] = useState(false);
  const [editing, setEditing] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("access_token");

    if (!token) {
      router.push("/login");
      return;
    }

    loadProfile(token);
  }, [router]);

  async function loadProfile(token: string) {
    try {
      const response = await fetch(`${API_URL}/api/profile`, {
        method: "GET",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      const data = await response.json();

      console.log("Profile response:", data);

      if (!response.ok) {
        throw new Error(data.error || "Failed to load profile");
      }

      setUser({ email: data.email, ...(data.profile || {}) });
    } catch (error) {
      console.error("Profile error:", error);
    } finally {
      setLoading(false);
    }
  }
  function logout() {
    localStorage.removeItem("access_token");
    router.push("/login");
  }

  function initials(name?: string) {
    if (!name) return "?";

    return name
      .trim()
      .split(/\s+/)
      .slice(0, 2)
      .map((part) => part[0].toUpperCase())
      .join("");
  }

  async function saveProfile(
    e: React.FormEvent<HTMLFormElement>,
    mode: ProfileMode,
  ) {
    e.preventDefault();

    const token = localStorage.getItem("access_token");

    if (!token) return;

    try {
      setCreating(mode === "create");
      setEditing(mode === "edit");

      let imageUrl = "";

      // Upload new image if selected
      if (image) {
        const formData = new FormData();
        formData.append("image", image);

        const uploadResponse = await fetch(`${API_URL}/api/upload_image`, {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
          },
          body: formData,
        });

        const uploadData = await uploadResponse.json();

        if (!uploadResponse.ok) {
          throw new Error(uploadData.error || "Failed to upload image");
        }

        imageUrl = uploadData.image_url;
      }
      console.log(imageUrl)
      // CREATE
      if (mode === "create") {
        const response = await fetch(`${API_URL}/api/create_profile`, {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            name,
            bio,
            image_url: imageUrl,
          }),
        });

        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.error || "Failed to create profile");
        }

        console.log("Profile created:", data);
      }

      // EDIT
      if (mode === "edit") {
        const response = await fetch(`${API_URL}/api/edit_profile`, {
          method: "PATCH",
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            name,
            bio,
            ...(imageUrl && { image_url: imageUrl }),
          }),
        });

        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.error || "Failed to edit profile");
        }

        console.log("Profile edited:", data);
      }

      setShowProfileForm(false);
      setShowProfileEditForm(false);

      await loadProfile(token);
    } catch (error) {
      console.error("Profile error:", error);
    } finally {
      setCreating(false);
      setEditing(false);
    }
  }

  if (loading) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-[#171613]">
        <p className="font-mono text-xs tracking-wider text-white/50">
          LOADING YOUR FOLIO...
        </p>
      </main>
    );
  }

  if (!user) {
    return null;
  }

  const fields = [user.name, user.email, user.bio, user.image_url];

  const completedFields = fields.filter(Boolean).length;
  const profileCompletion = Math.round((completedFields / fields.length) * 100);

  return (
    <main className="min-h-screen bg-[#171613] px-5 py-7 text-[#f3efe3] sm:px-8">
      <div className="mx-auto max-w-[1040px]">
        {/* TOP BAR */}
        <header className="mb-7 flex items-center justify-between border-b border-white/10 px-1 pb-5">
          <Link
            href="/"
            className="font-serif text-[22px] font-medium tracking-tight"
          >
            fol<span className="text-[#56a89b]">io</span>
          </Link>

          <div className="flex items-center gap-4 sm:gap-6">
            <span className="hidden font-mono text-[10px] tracking-widest text-white/40 sm:block">
              {new Date()
                .toLocaleDateString("en-US", {
                  month: "short",
                  day: "2-digit",
                  year: "numeric",
                })
                .toUpperCase()}
            </span>

            <button
              onClick={logout}
              className="rounded-sm border border-white/10 px-3.5 py-2 font-mono text-[10px] uppercase tracking-wider text-white/70 transition hover:border-[#b5651d] hover:text-[#f3efe3]"
            >
              Sign out
            </button>
          </div>
        </header>

        {/* DASHBOARD GRID */}
        <div className="grid gap-5 md:grid-cols-[320px_1fr]">
          {/* PROFILE CARD */}

          {showProfileForm && (
            <CreateEditComponent
              onClick={() => setShowProfileForm(false)}
              onSubmit={(e) => saveProfile(e, "create")}
              name={name}
              setName={setName}
              bio={bio}
              setBio={setBio}
              image={image}
              setImage={setImage}
              creating={creating}
              mode="create"
            />
          )}
          {showProfileEditForm && (
            <CreateEditComponent
              onClick={() => setShowProfileEditForm(false)}
              onSubmit={(e) => saveProfile(e, "edit")}
              name={name}
              setName={setName}
              bio={bio}
              setBio={setBio}
              image={image}
              setImage={setImage}
              creating={editing}
              mode="edit"
            />
          )}
          <section className="rounded bg-[#f3efe3] p-7 text-center text-[#1f1b16]">
            {/* Avatar */}
            <div className="mx-auto mb-4 flex h-[84px] w-[84px] items-center justify-center overflow-hidden rounded-full border border-black/10 bg-[#e4e0d2] font-serif text-[28px] text-black/40">
              {user.image_url ? (
                <img
                  src={user.image_url}
                  alt={user.name || "Profile photo"}
                  className="h-full w-full object-cover"
                />
              ) : (
                initials(user.name)
              )}
            </div>

            <h2 className="font-serif text-[21px] font-medium">
              {user.name || "Your Name"}
            </h2>

            <p className="mt-1 font-mono text-xs text-black/50">
              {user.email || "—"}
            </p>

            <p className="mt-5 text-[13.5px] leading-relaxed text-black/70">
              {user.bio || (
                <span className="italic text-black/35">
                  No bio yet — add a line about your work.
                </span>
              )}
            </p>

            <button
              onClick={() => setShowProfileForm((prev) => !prev)}
              className="mt-5 w-full rounded-sm bg-[#1f1b16] py-3 font-mono text-[11px] uppercase tracking-wider text-[#f3efe3] transition hover:bg-[#33291d]"
            >
              create profile
            </button>
            <button
              onClick={() => setShowProfileEditForm((prev) => !prev)}
              className="mt-5 w-full rounded-sm bg-[#1f1b16] py-3 font-mono text-[11px] uppercase tracking-wider text-[#f3efe3] transition hover:bg-[#33291d]"
            >
              Edit profile
            </button>

            <div className="my-5 h-px w-full bg-black/10" />

            <div className="mb-2 flex justify-between font-mono text-[11px] text-black/50">
              <span>Member since</span>

              <span className="text-[#1f1b16]">
                {user.created_at
                  ? new Date(user.created_at).toLocaleDateString("en-US", {
                      month: "short",
                      year: "numeric",
                    })
                  : "—"}
              </span>
            </div>

            <div className="flex justify-between font-mono text-[11px] text-black/50">
              <span>Status</span>
              <span className="text-[#3e7c74]">Active</span>
            </div>
            <div>
              <button
                onClick={() => {
                  router.push("/dashboard");
                }}
                className="mb-6 text-sm text-black/50 hover:text-black"
              >
                ← Back to dashboard
              </button>
            </div>
          </section>
          {/* RIGHT SIDE */}
          <div className="flex flex-col gap-5">
            {/* WELCOME */}
            <section className="rounded bg-[#f3efe3] p-7 text-[#1f1b16]">
              <h1 className="font-serif text-[24px] font-medium">
                Welcome back
                {user.name ? `, ${user.name.split(" ")[0]}` : ""}
              </h1>

              <p className="mt-1.5 text-[13.5px] text-black/60">
                Here&apos;s where your folio stands today.
              </p>
            </section>

            {/* STATS */}
            <section className="grid gap-5 sm:grid-cols-3">
              <div className="rounded bg-[#f3efe3] p-5 text-[#1f1b16]">
                <div className="font-serif text-[30px] font-medium text-[#3e7c74]">
                  {user.item_count ?? 0}
                </div>

                <div className="mt-2 font-mono text-[10.5px] uppercase tracking-wider text-black/50">
                  Portfolio items
                </div>
              </div>

              <div className="rounded bg-[#f3efe3] p-5 text-[#1f1b16]">
                <div className="font-serif text-[30px] font-medium text-[#3e7c74]">
                  {user.view_count ?? 0}
                </div>

                <div className="mt-2 font-mono text-[10.5px] uppercase tracking-wider text-black/50">
                  Profile views
                </div>
              </div>

              <div className="rounded bg-[#f3efe3] p-5 text-[#1f1b16]">
                <div className="font-serif text-[30px] font-medium text-[#3e7c74]">
                  {profileCompletion}%
                </div>

                <div className="mt-2 font-mono text-[10.5px] uppercase tracking-wider text-black/50">
                  Profile complete
                </div>
              </div>
            </section>

            {/* RECENT WORK */}
            <section className="rounded bg-[#f3efe3] p-6 text-[#1f1b16]">
              <div className="flex items-baseline justify-between">
                <h2 className="font-serif text-[17px] font-medium">
                  Recent work
                </h2>

                <span className="font-mono text-[10px] text-black/40">
                  PROOF SHEET
                </span>
              </div>

              <div className="my-4 h-px bg-black/10" />

              <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4">
                {/* Add project */}
                <button
                  onClick={() => router.push("/projects/new")}
                  className="aspect-square rounded-sm border border-dashed border-black/20 bg-[#ebe6d7] p-3 font-mono text-[10px] text-black/45 transition hover:border-[#3e7c74] hover:text-[#3e7c74]"
                >
                  + Add your first piece
                </button>

                {/* Empty placeholders */}
                {[1, 2, 3].map((item) => (
                  <div
                    key={item}
                    className="flex aspect-square items-center justify-center rounded-sm border border-dashed border-black/15 bg-[#ebe6d7] p-3 text-center font-mono text-[10px] text-black/25"
                  >
                    FRAME {String(item).padStart(2, "0")}
                  </div>
                ))}
              </div>
            </section>
          </div>
        </div>

        {/* QUICK ACTIONS */}
        <section className="mt-5 grid gap-5 sm:grid-cols-3">
          <button
            onClick={() => router.push("/exercises")}
            className="rounded bg-[#201f1b] p-5 text-left transition hover:bg-[#282721]"
          >
            <span className="font-mono text-[10px] uppercase tracking-widest text-[#56a89b]">
              01
            </span>

            <h3 className="mt-3 font-serif text-lg">Exercises</h3>

            <p className="mt-1 text-xs leading-relaxed text-white/45">
              Test your understanding with hands-on technical exercises.
            </p>
          </button>

          <button
            onClick={() => router.push("/projects")}
            className="rounded bg-[#201f1b] p-5 text-left transition hover:bg-[#282721]"
          >
            <span className="font-mono text-[10px] uppercase tracking-widest text-[#56a89b]">
              02
            </span>

            <h3 className="mt-3 font-serif text-lg">Projects</h3>

            <p className="mt-1 text-xs leading-relaxed text-white/45">
              Build projects and prove what you can actually do.
            </p>
          </button>

          <button
            onClick={() => router.push("/reviews")}
            className="rounded bg-[#201f1b] p-5 text-left transition hover:bg-[#282721]"
          >
            <span className="font-mono text-[10px] uppercase tracking-widest text-[#56a89b]">
              03
            </span>

            <h3 className="mt-3 font-serif text-lg">Code reviews</h3>

            <p className="mt-1 text-xs leading-relaxed text-white/45">
              Get feedback on your code and improve your engineering skills.
            </p>
          </button>
        </section>
      </div>
    </main>
  );
}
