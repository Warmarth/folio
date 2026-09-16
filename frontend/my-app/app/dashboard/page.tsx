"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

type Profile = { id: string; name?: string; email?: string; bio?: string; image?: string };
const API_URL = process.env.NEXT_PUBLIC_API_URL;

export default function DashboardPage() {
  const [profiles, setProfiles] = useState<Profile[]>([]);
  const router = useRouter();

  console.log(profiles);

  async function loadProfiles() {
    const token = localStorage.getItem("access_token");

    if (!token) {
      console.log("No access token");
      return;
    }

    try {
      const response = await fetch(`${API_URL}/api/all_profile`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Failed to load profiles");
      }

      setProfiles(data.data);
    } catch (error) {
      console.error("Profiles error:", error);
    }
  }

  useEffect(() => {
    const timeoutId = window.setTimeout(() => {
      void loadProfiles();
    }, 0);
    return () => window.clearTimeout(timeoutId);
  }, []);

  return (
    <>
      <h1 className="font-serif text-3xl">Folio Dashboard</h1>

      <div className="mt-8">
        <h2 className="text-xl font-serif mb-4 text-black/700">All Users</h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {profiles.map((profile) => (
            <div
              key={profile.id}
              onClick={() => {
                router.push(`/dashboard/user/${profile.id}`);
              }}
              className="bg-white border border-black/10 rounded-lg p-5 cursor-pointer hover:border-[#3e7c74] transition"
            >
              <div className="flex items-center gap-4">
                {profile.image ? (
                  <img
                    src={profile.image}
                    alt={profile.name || "Profile"}
                    className="w-12 h-12 rounded-full object-cover"
                  />
                ) : (
                  <div className="w-12 h-12 rounded-full bg-[#171613] text-[#f3efe3] flex items-center justify-center">
                    {profile.name?.charAt(0).toUpperCase() || "?"}
                  </div>
                )}

                <div>
                  <h3 className="font-medium">{profile.name || "Unnamed"}</h3>
                  <p className="text-xs text-black/40 mt-1">
                    {profile.email || "No email"}
                  </p>

                  <p className="text-sm text-black/50 mt-1">
                    {profile.bio || "No bio yet."}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </>
  );
}
