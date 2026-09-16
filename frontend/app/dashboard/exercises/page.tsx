"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

const API_URL = process.env.NEXT_PUBLIC_API_URL;

type Exercise = {
  id: string;
  title: string;
  created_at?: string;
  level?: string;
  description?: string;
};

export default function ExercisesPage() {
  const [exercises, setExercises] = useState<Exercise[]>([]);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    async function loadExercises() {
      const token = localStorage.getItem("access_token");

      if (!token) {
        console.log("No access token");
        return;
      }

      try {
        const response = await fetch(
          `${API_URL}/api/exercises/all_exercise?page=1&per_pages=10`,
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          },
        );

        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.error || "Failed to load exercises");
        }
        console.log(data);
        setExercises(data.data);
      } catch (error) {
        console.error("Exercises error:", error);
      } finally {
        setLoading(false);
      }
    }

    loadExercises();
  }, []);

  if (loading) {
    return <main className="p-8">Loading exercises...</main>;
  }

  return (
    <div className="grid gap-4">
      <h2>Exercises</h2>
      {exercises.length > 0 ? (
        exercises.map((exercise) => (
          <div
            key={exercise.id}
            className="bg-white border border-black/10 rounded-lg p-5 cursor-pointer"
            onClick={() => {
              router.push(`/dashboard/exercises/${exercise.id}`);
            }}
          >
            <h2 className="text-lg font-medium">{exercise.title}</h2>

            <div className="flex gap-2 mt-2 text-xs">
              {exercise.created_at && (
                <span className="px-2 py-1 bg-[#ebe6d7] rounded">
                  {exercise.created_at}
                </span>
              )}

              {exercise.level && (
                <span className="px-2 py-1 bg-[#ebe6d7] rounded">
                  {exercise.level}
                </span>
              )}
            </div>

            {exercise.description && (
              <p className="text-sm text-black/50 mt-3">
                {exercise.description}
              </p>
            )}
          </div>
        ))
      ) : (
        <p>No exercises</p>
      )}
    </div>
  );
}
