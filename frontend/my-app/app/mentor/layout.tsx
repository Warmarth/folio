"use client";

import { useEffect, useState } from "react";
import {
  LayoutDashboard,
  BookOpen,
  FileText,
  Users,
  BarChart3,
  Settings,
} from "lucide-react";
import { usePathname, useRouter } from "next/navigation";
import NavItem from "./components/NavItem";

interface UserInfo {
  name?: string;
  email?: string;
  image_url?: string;
  profile?: {
    name?: string;
    bio?: string;
    image_url?: string;
  };
}

export default function MentorLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const pathname = usePathname();

  const [userInfo, setUserInfo] = useState<UserInfo>({});

  function logout() {
    localStorage.removeItem("access_token");
    router.push("/login");
  }

  async function getUserInfo() {
    const token = localStorage.getItem("access_token");

    if (!token) {
      console.log("No access token");
      return;
    }

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/mentors_profile`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        },
      );

      const data = await response.json();

      if (!response.ok) {
        console.error("Failed to fetch mentor:", data);
        return;
      }

      setUserInfo(data);
      console.log(data);
    } catch (error) {
      console.error("Error fetching mentor:", error);
    }
  }

  useEffect(() => {
    const timeoutId = window.setTimeout(() => {
      void getUserInfo();
    }, 0);
    return () => window.clearTimeout(timeoutId);
  }, []);

  return (
    <div className="h-screen overflow-hidden bg-gray-50 text-gray-900">
      {/* Sidebar */}
      <aside className="fixed left-0 top-0 hidden h-screen w-64 border-r bg-white p-5 md:block">
        <div className="mb-10">
          <h1 className="text-2xl font-bold">Folio</h1>
          <p className="text-sm text-gray-500">Mentor Portal</p>
        </div>

        <nav className="space-y-2">
          <NavItem
            icon={<LayoutDashboard size={19} />}
            label="Dashboard"
            active={pathname === "/mentor/dashboard"}
            onClick={() => router.push("/mentor/dashboard")}
          />

          <NavItem
            icon={<BookOpen size={19} />}
            label="Exercises"
            active={pathname === "/mentor/exercises"}
            onClick={() => router.push("/mentor/exercises")}
          />

          <NavItem
            icon={<FileText size={19} />}
            label="Submissions"
            active={pathname === "/mentor/submissions"}
            onClick={() => router.push("/mentor/submissions")}
          />

          <NavItem
            icon={<Users size={19} />}
            label="Learners"
            active={pathname === "/mentor/learners"}
            onClick={() => router.push("/mentor/learners")}
          />

          <NavItem
            icon={<BarChart3 size={19} />}
            label="Performance"
            active={pathname === "/mentor/performance"}
            onClick={() => router.push("/mentor/performance")}
          />

          <NavItem
            icon={<Settings size={19} />}
            label="Settings"
            active={pathname === "/mentor/settings"}
            onClick={() => router.push("/mentor/settings")}
          />
        </nav>

        {/* Mentor profile */}
        <div className="absolute bottom-5 left-5 right-5 rounded-xl bg-gray-100 p-4">
          <div className="mb-3">
            {userInfo?.profile?.image_url ? (
              <img
                src={userInfo.profile.image_url}
                alt="Mentor"
                className="h-10 w-10 rounded-full object-cover"
              />
            ) : (
              <div className="flex h-10 w-10 items-center justify-center rounded-full bg-black text-white">
                {userInfo?.profile?.name?.charAt(0).toUpperCase() || "M"}
              </div>
            )}
          </div>

          <p className="font-semibold">{userInfo?.profile?.name || "Mentor"}</p>

          <p className="truncate text-sm text-gray-500">
            {userInfo?.email || "mentor@example.com"}
          </p>
        </div>
        <button
          onClick={logout}
          className="rounded-lg bg-black px-4 py-2 text-sm font-medium text-white hover:bg-gray-800"
        >
          Sign out
        </button>
      </aside>

      {/* Main area */}
      <div className="ml-64 h-screen">
        {/* Fixed Header */}
        <header className="fixed left-64 right-0 top-0 z-50 h-20 border-b bg-white">
          <div className="flex h-full items-center justify-between px-6">
            <div>
              <p className="text-sm text-gray-500">Mentor Dashboard</p>

              <h2 className="text-xl font-bold">Good evening 👋</h2>
            </div>

            <button
              onClick={() => router.push("/mentor/dashboard/create_exercise")}
              className="rounded-lg bg-black px-4 py-2 text-sm font-medium text-white hover:bg-gray-800"
            >
              + Create Exercise
            </button>
          </div>
        </header>

        {/* Scrollable content */}
        <main className="h-screen overflow-y-auto pt-20">
          <div className="p-6">{children}</div>
        </main>
      </div>
    </div>
  );
}
