"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";

const API_URL = process.env.NEXT_PUBLIC_API_URL;

export default function LearnersLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const [user, setUser] = useState<{
    name?: string;
    email?: string;
    image_url?: string;
  }>({});
  
  const router = useRouter();


   function logout() {
    localStorage.removeItem("access_token");
    router.push("/login");
  }

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
    }
    loadUser();
  }, []);
 
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

          <Link
            href="/dashboard/exercises"
            className="block px-3 py-2 text-sm text-white/70 hover:bg-white/5 rounded"
          >
            ▤ Exercises
          </Link>

          <Link
            href="/dashboard/projects"
            className="block px-3 py-2 text-sm text-white/70 hover:bg-white/5 rounded"
          >
            ▦ Projects
          </Link>

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

          <Link
            href="/dashboard/mentorship"
            className="block px-3 py-2 text-sm text-white/70 hover:bg-white/5 rounded"
          >
            ◎ Mentorship
          </Link>

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
              {user.image_url ? (
                <img
                  src={user.image_url}
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

          <button
            className="mt-4 text-[10px] uppercase tracking-wider text-white/40 hover:text-[#b5651d]"
            onClick={ logout}
          >
            Sign out
          </button>
        </div>
      </aside>
      <main className="flex-1 p-8 ">{children}</main>
    </div>
  );
}
