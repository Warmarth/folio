"use client";
import { useEffect, useState } from "react";

export default function DashboardPage() {
  const [user, setUser] = useState<{
    name?: string;
    email?: string;
    image?: string;
  }>({});
  const [profiles, setProfiles] = useState<any[]>([]);

  const API_URL = process.env.NEXT_PUBLIC_API_URL;

  useEffect(() => {
    async function loadUser() {
      const token = localStorage.getItem("access_token");

      if (!token) {
        console.log("No access token");
        return;
      }

      try {
        const response = await fetch(`${API_URL}/api/profile`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.error || "Failed to load profile");
        }

        setUser({ email: data.email, ...(data.profile || {}) });
      } catch (error) {
        console.error("Dashboard profile error:", error);
      }
      await loadProfiles();
    }

    loadUser();
  }, []);

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

  return (
    <div className="min-h-screen flex bg-[#f3efe3]">
      {/* Sidebar */}
      <aside className="w-60 min-h-screen bg-[#171613] text-[#f3efe3] p-5 flex flex-col">
        {/* Brand */}
        <div className="text-2xl font-serif px-2 pb-8">
          fol<span className="text-[#56a89b]">io</span>
        </div>

        {/* Learn */}
        <div className="mb-6">
          <p className="text-[10px] uppercase tracking-widest text-white/30 px-2 mb-2">
            Learn
          </p>

          <a
            href="/dashboard/exercises"
            className="block px-3 py-2 text-sm text-white/70 hover:bg-white/5 rounded"
          >
            ▤ Exercises
          </a>

          <a
            href="/dashboard/projects"
            className="block px-3 py-2 text-sm text-white/70 hover:bg-white/5 rounded"
          >
            ▦ Projects
          </a>

          <a
            href="/dashboard/code-review"
            className="block px-3 py-2 text-sm text-white/70 hover:bg-white/5 rounded"
          >
            ⌥ Code review
          </a>
        </div>

        {/* Grow */}
        <div className="mb-6">
          <p className="text-[10px] uppercase tracking-widest text-white/30 px-2 mb-2">
            Grow
          </p>

          <a
            href="/dashboard/mentorship"
            className="block px-3 py-2 text-sm text-white/70 hover:bg-white/5 rounded"
          >
            ◎ Mentorship
          </a>

          <a
            href="/dashboard/progress"
            className="block px-3 py-2 text-sm text-white/70 hover:bg-white/5 rounded"
          >
            ▲ Progress
          </a>
        </div>

        {/* Account */}
        <div className="mb-6">
          <p className="text-[10px] uppercase tracking-widest text-white/30 px-2 mb-2">
            Account
          </p>

          <a
            href="/me"
            className="block px-3 py-2 text-sm text-white/70 hover:bg-white/5 rounded"
          >
            ● Profile
          </a>

          <a
            href="/dashboard/settings"
            className="block px-3 py-2 text-sm text-white/70 hover:bg-white/5 rounded"
          >
            ⚙ Settings
          </a>
        </div>

        {/* Push user section to bottom */}
        <div className="flex-1" />

        {/* User */}
        <div className="border-t border-white/10 pt-4 px-2">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-full bg-white/10 flex items-center justify-center">
              {user.image ? (
                <img
                  src={user.image}
                  alt={user.name || "Profile photo"}
                  className="h-full w-full object-cover"
                />
              ) : (
                <p> ?</p>
              )}
            </div>
            <p className="text-sm truncate">{user.name || "Unnamed"}</p>

            <p className="text-[10px] text-white/40 truncate">
              {user.email || "—"}
            </p>
          </div>

          <button className="mt-4 text-[10px] uppercase tracking-wider text-white/40 hover:text-[#b5651d]">
            Sign out
          </button>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 p-8 ">
        <h1 className="font-serif text-3xl">Folio Dashboard</h1>

        <div className="mt-8">
          <h2 className="text-xl font-serif mb-4 text-black/700">All Users</h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {profiles.map((profile) => (
              <div
                key={profile.id}
                onClick={() => {
                  window.location.href = `/dashboard/user/${profile.id}`;
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
      </main>
    </div>
  );
}
