"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import SubmitExercise from "@/app/components/submitExercise";

type Exercise = { title?: string; description?: string };

export default function ExerciseDetailsPage() {
  const params = useParams();
  const id = params.id as string;

  const [exercise, setExercise] = useState<Exercise | null>(null);
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [submitPage, setSubmitPage] = useState(false);

  const API_URL = process.env.NEXT_PUBLIC_API_URL;

  useEffect(() => {
    async function loadExercise() {
      const token = localStorage.getItem("access_token");

      if (!token) {
        console.log("No access token");
        return;
      }

      try {
        const response = await fetch(
          `${API_URL}/api/exercises/all_exercise/${id}`,
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          },
        );

        const data = await response.json();

        if (!response.ok) {
          throw new Error(
            data.error || "Failed to load exercise"
          );
        }

        setExercise(data.data);
      } catch (error) {
        console.error("Exercise error:", error);
      } finally {
        setLoading(false);
      }
    }

    if (id) {
      loadExercise();
    }
  }, [id, API_URL]);

  if (loading) {
    return <main className="p-8">Loading exercise...</main>;
  }

  if (!exercise) {
    return <main className="p-8">Exercise not found.</main>;
  }

  return (
    <main className="min-h-screen bg-[#f3efe3] p-8">
      <h1 className="text-3xl font-serif">{exercise.title}</h1>

      <p className="mt-4">{exercise.description}</p>

      <button
        type="button"
        className="mt-4 bg-[#1f1b16] text-[#f3efe3] px-4 py-2 rounded"
        onClick={() => {
          setSubmitPage((p) => !p);
        }}
      >
        {submitPage ? "Close submission" : "Click to submit your exercise"}
      </button>

      {submitPage && <SubmitExercise exerciseId={id} />}
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
