"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";

const API_URL = process.env.NEXT_PUBLIC_API_URL;

type Profile = {
  id: string;
  name?: string;
  email?: string;
  bio?: string;
  image?: string;
  created_at?: string;
};

export default function UserProfilePage() {
  const params = useParams();
  const id = params.id as string;

  const [profile, setProfile] = useState<Profile | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    async function loadProfile() {
      const token = localStorage.getItem("access_token");

      if (!token) {
        console.log("No access token");
        return;
      }

      try {
        const response = await fetch(`${API_URL}/api/all_profile/${id}`, {
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        });

        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.error || "Failed to load profile");
        }

        setProfile(data.data);
      } catch (error) {
        console.error("Profile error:", error);
      } finally {
        setLoading(false);
      }
    }

    if (id) {
      loadProfile();
    }
  }, [id]);

  if (loading) {
    return (
      <main className="min-h-screen bg-[#f3efe3] p-8">Loading profile...</main>
    );
  }

  if (!profile) {
    return (
      <main className="min-h-screen bg-[#f3efe3] p-8">Profile not found.</main>
    );
  }

  return (
    <main className="min-h-screen bg-[#f3efe3] p-8">
      <div className="max-w-xl bg-white border border-black/10 rounded-lg p-6">
        {profile.image ? (
          <img
            src={profile.image}
            alt={profile.name || "Profile"}
            className="w-24 h-24 rounded-full object-cover"
          />
        ) : (
          <div className="w-24 h-24 rounded-full bg-[#171613] text-[#f3efe3] flex items-center justify-center text-2xl">
            {profile.name?.charAt(0).toUpperCase() || "?"}
          </div>
        )}

        <h1 className="text-2xl font-serif mt-5">
          {profile.name || "Unnamed"}
        </h1>

        <p className="text-sm text-black/40 mt-1">
          {profile.email || "No email"}
        </p>

        <p className="mt-5 text-black/60">{profile.bio || "No bio yet."}</p>
      </div>
      <button
        onClick={() => {
          router.push("/dashboard");
        }}
        className="mb-6 text-sm text-black/50 hover:text-black"
      >
        ← Back to dashboard
      </button>
    </main>
  );
}
