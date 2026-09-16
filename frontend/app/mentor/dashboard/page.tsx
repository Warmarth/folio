"use client";

import {
  BookOpen,
  FileText,
  Users,
  BarChart3,
  CheckCircle2,
} from "lucide-react";
import StatCard from "../components/StatCard";
import Exercise from "../components/Exercise";
import Activity from "../components/Activty";
import Submission from "../components/submission";
import { useEffect, useState } from "react";

type ExerciseData = {
  id: string;
  title?: string;
  description?: string;
  level?: string;
  xp_points?: number;
};

type SubmissionData = {
  id: string;
  user_name?: string;
  exercise_name?: string;
  submitted_at?: string;
};

export default function MentorDashboard() {
  const [exercises, setExercises] = useState<ExerciseData[]>([]);
  const [submitted, setSubmitted] = useState<SubmissionData[]>([]);

  useEffect(() => {
    async function loadExercises() {
      const token = localStorage.getItem("access_token");
      if (!token) return;

      try {
        const res = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL}/api/exercises/all_exercise/mentor`,
          {
            headers: {
              Authorization: `Bearer ${token}`,
              "Content-Type": "application/json",
            },
          },
        );
        if (!res.ok) throw new Error(`Exercises fetch failed: ${res.status}`);
        const data = await res.json();
        setExercises(data.data || []);
      } catch (err) {
        console.error("Error loading exercises:", err);
      }
    }

    async function loadSubmissions() {
      const token = localStorage.getItem("access_token");
      if (!token) return;

      try {
        const res = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL}/api/submit/submitted_exercise`,
          {
            headers: {
              Authorization: `Bearer ${token}`,
              "Content-Type": "application/json",
            },
          },
        );
        if (!res.ok) throw new Error(`Submissions fetch failed: ${res.status}`);
        const data = await res.json();
        console.log(data.data);
        setSubmitted(data.data || []);
      } catch (err) {
        console.error("Error loading submissions:", err);
      }
    }

    loadExercises();
    loadSubmissions();
  }, []);


  return (
    <div className="min-h-screen bg-gray-50 text-gray-900">
      <div className="flex">
        {/* Main */}
        <main className="w-full p-5 md:p-8">
          {/* Stats */}
          <div className="mb-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <StatCard
              title="Exercises"
              value={String(exercises.length)}
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
                {exercises.length > 0 ? (
                  exercises.map((exercise) => (
                    <Exercise
                      key={exercise.id}
                      title={exercise.title || ""}
                      description={exercise.description || ""}
                      level={exercise.level || ""}
                      xp_reward={exercise.xp_points || 0}
                    />
                  ))
                ) : (
                  <div>No exercises available.</div>
                )}
              </div>
            </section>

            {/* Recent Activity */}
            <section className="rounded-xl border bg-white p-5">
              <div className="mb-5">
                <h3 className="font-semibold">Recent Activity</h3>
                <p className="text-sm text-gray-500">Latest learner activity</p>
              </div>

              <div className="space-y-5">
                {submitted.map((submit) => (
                  <Activity
                    key={submit.id}
                    icon={<CheckCircle2 size={18} />}
                    text={`${submit.user_name} submitted ${submit.exercise_name}`}
                    time={submit.submitted_at ?? ""}
                  />
                ))}
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
                </tbody>
              </table>
            </div>
          </section>
        </main>
      </div>
    </div>
  );
}
