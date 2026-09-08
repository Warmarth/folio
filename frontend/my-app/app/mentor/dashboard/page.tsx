"use client";

import {
  LayoutDashboard,
  BookOpen,
  FileText,
  Users,
  BarChart3,
  Settings,
  Plus,
  CheckCircle2,
  Clock3,
} from "lucide-react";
import { useEffect, useState } from "react";
import NavItem from "../components/NavItem";
import StatCard from "../components/StatCard";
import Exercise from "../components/Exercise";
import Activity from "../components/Activty";
import Submission from "../components/submission";
import { usePathname, useRouter } from "next/navigation";

interface MentorDashboardProps {
  name?: string;
  email?: string;
  image?: string;
}

interface UserInfo {
  name?: string;
  email?: string;
  image?: string;
  mentor?: {
    name?: string;
    email?: string;
    image?: string;
  };
}

export default function MentorDashboard({
  name,
  email,
  image,
}: MentorDashboardProps) {
  const [userInfo, setUserInfo] = useState<UserInfo>({
    name,
    email,
    image,
  });

  const router = useRouter(); // Ensure router is defined
  const pathname = usePathname(); // Ensure pathname is defined

  useEffect(() => {
    getUserInfo();
  }, []);

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
        console.error("Failed to fetch user info:", data);
        return;
      }

      console.log("User info fetched successfully:", data);
      setUserInfo(data);
    } catch (error) {
      console.error("Error fetching user info:", error);
    }
  }
  return (
    <div className="min-h-screen bg-gray-50 text-gray-900">
      <div className="flex">
        {/* Sidebar */}
        <aside className="hidden min-h-screen w-64 border-r bg-white p-5 md:block">
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
              active={pathname.startsWith("/mentor/exercises")}
              onClick={() => router.push("/mentor/exercises")}
            />

            <NavItem
              icon={<FileText size={19} />}
              label="Submissions"
              active={pathname.startsWith("/mentor/submissions")}
              onClick={() => router.push("/mentor/submissions")}
            />

            <NavItem
              icon={<Users size={19} />}
              label="Learners"
              active={pathname.startsWith("/mentor/learners")}
              onClick={() => router.push("/mentor/learners")}
            />

            <NavItem
              icon={<BarChart3 size={19} />}
              label="Performance"
              active={pathname.startsWith("/mentor/performance")}
              onClick={() => router.push("/mentor/performance")}
            />

            <NavItem
              icon={<Settings size={19} />}
              label="Settings"
              active={pathname.startsWith("/mentor/settings")}
              onClick={() => router.push("/mentor/settings")}
            />
          </nav>

          <div className="mt-16 rounded-xl bg-gray-100 p-4">
            <div className="mb-3 flex h-10 w-10 items-center justify-center rounded-full bg-black text-white">
              {userInfo?.mentor?.image ? (
                <img
                  src={userInfo?.mentor?.image}
                  className="h-10 w-10 rounded-full object-cover"
                  alt="Mentor"
                  width={40}
                  height={40}
                />
              ) : (
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-black text-white">
                  {userInfo?.mentor?.name?.charAt(0).toUpperCase() || "M"}
                </div>
              )}
            </div>
            <p className="font-semibold">
              {userInfo?.mentor?.name || "Mentor"}
            </p>
            <p className="text-sm text-gray-500">
              {userInfo?.mentor?.email || "mentor@example.com"}
            </p>
          </div>
        </aside>

        {/* Main */}
        <main className="w-full p-5 md:p-8">
          {/* Header */}
          <div className="mb-8 flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Mentor Dashboard</p>
              <h2 className="mt-1 text-2xl font-bold md:text-3xl">
                Good evening 👋
              </h2>
              <p className="mt-1 text-gray-500">
                Here's what's happening with your learners.
              </p>
            </div>

            <button
              className="flex items-center gap-2 rounded-lg bg-black px-4 py-2.5 text-sm font-medium text-white hover:bg-gray-800"
              onClick={() => router.push("/mentor/dashboard/create_exercise")}
            >
              <Plus size={18} />
              Create Exercise
            </button>
          </div>

          {/* Stats */}
          <div className="mb-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <StatCard
              title="Exercises"
              value="12"
              description="+2 this month"
              icon={<BookOpen size={20} />}
            />

            <StatCard
              title="Submissions"
              value="48"
              description="+14 this week"
              icon={<FileText size={20} />}
            />

            <StatCard
              title="Learners"
              value="36"
              description="+5 this month"
              icon={<Users size={20} />}
            />

            <StatCard
              title="Average Score"
              value="78%"
              description="+6% this month"
              icon={<BarChart3 size={20} />}
            />
          </div>

          {/* Content grid */}
          <div className="grid gap-6 lg:grid-cols-3">
            {/* Exercises */}
            <section className="rounded-xl border bg-white p-5 lg:col-span-2">
              <div className="mb-5 flex items-center justify-between">
                <div>
                  <h3 className="font-semibold">Your Exercises</h3>
                  <p className="text-sm text-gray-500">
                    Manage your learning exercises
                  </p>
                </div>

                <button className="text-sm font-medium text-gray-600 hover:text-black">
                  View all
                </button>
              </div>

              <div className="space-y-3">
                <Exercise
                  title="REST API Fundamentals"
                  category="Backend"
                  submissions="18 submissions"
                />

                <Exercise
                  title="Python Functions"
                  category="Python"
                  submissions="12 submissions"
                />

                <Exercise
                  title="SQL Basics"
                  category="Database"
                  submissions="8 submissions"
                />

                <Exercise
                  title="Git & GitHub"
                  category="Development"
                  submissions="10 submissions"
                />
              </div>
            </section>

            {/* Recent Activity */}
            <section className="rounded-xl border bg-white p-5">
              <div className="mb-5">
                <h3 className="font-semibold">Recent Activity</h3>
                <p className="text-sm text-gray-500">Latest learner activity</p>
              </div>

              <div className="space-y-5">
                <Activity
                  icon={<CheckCircle2 size={18} />}
                  text="John completed REST API Fundamentals"
                  time="10 min ago"
                />

                <Activity
                  icon={<CheckCircle2 size={18} />}
                  text="Sarah submitted Python Functions"
                  time="1 hour ago"
                />

                <Activity
                  icon={<Clock3 size={18} />}
                  text="Mike started SQL Basics"
                  time="2 hours ago"
                />

                <Activity
                  icon={<CheckCircle2 size={18} />}
                  text="David scored 92% on Git & GitHub"
                  time="4 hours ago"
                />
              </div>
            </section>
          </div>

          {/* Submissions */}
          <section className="mt-6 rounded-xl border bg-white p-5">
            <div className="mb-5 flex items-center justify-between">
              <div>
                <h3 className="font-semibold">Recent Submissions</h3>
                <p className="text-sm text-gray-500">
                  Review learner submissions
                </p>
              </div>

              <button className="text-sm font-medium text-gray-600 hover:text-black">
                View all
              </button>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full min-w-[600px] text-left text-sm">
                <thead>
                  <tr className="border-b text-gray-500">
                    <th className="pb-3 font-medium">Learner</th>
                    <th className="pb-3 font-medium">Exercise</th>
                    <th className="pb-3 font-medium">Score</th>
                    <th className="pb-3 font-medium">Status</th>
                    <th className="pb-3"></th>
                  </tr>
                </thead>

                <tbody>
                  <Submission
                    learner="John Doe"
                    exercise="REST API Fundamentals"
                    score="85%"
                  />

                  <Submission
                    learner="Sarah Kim"
                    exercise="Python Functions"
                    score="92%"
                  />

                  <Submission
                    learner="Mike Johnson"
                    exercise="SQL Basics"
                    score="71%"
                  />

                  <Submission
                    learner="David Smith"
                    exercise="Git & GitHub"
                    score="88%"
                  />
                </tbody>
              </table>
            </div>
          </section>
        </main>
      </div>
    </div>
  );
}
