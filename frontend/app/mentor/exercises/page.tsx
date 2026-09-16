"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Exercise from "../components/Exercise";

interface ExerciseData {
  id?: string;
  title?: string;
  description?: string;
  level?: string;
  xp_points?: number;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL;

const ExercisesPage = () => {
  const [exercises, setExercises] = useState<ExerciseData[]>([]);
  const router = useRouter();

  useEffect(() => {
    const fetchExercises = async () => {
      const token = localStorage.getItem("access_token");

      if (!token) {
        console.log("No access token");
        return;
      }

      try {
        const response = await fetch(
          `${API_URL}/api/exercises/all_exercise/mentor`,
          {
            headers: {
              Authorization: `Bearer ${token}`,
              "Content-Type": "application/json",
            },
          },
        );

        if (!response.ok) {
          throw new Error("Failed to fetch exercises");
        }

        const data = await response.json();

        console.log("Fetched exercises:", data);

        setExercises(data.data || []);
      } catch (error) {
        console.error("Error fetching exercises:", error);
      }
    };

    fetchExercises();
  }, []);

  return (
    <div className="p-4">
      <h1 className="mb-4 text-2xl font-bold">Exercises</h1>

      <div className="grid grid-cols-1 gap-4">
        {exercises.length > 0 ? (
          exercises.map((exercise) => (
            <div key={exercise.id} onClick={() => router.push(`/mentor/exercises/${exercise.id}`)}>
              <Exercise
                key={exercise.id}
                title={exercise.title || ""}
                description={exercise.description || ""}
                level={exercise.level || ""}
                xp_reward={exercise.xp_points || 0}
              />
            </div>
          ))
        ) : (
          <div>No exercises available.</div>
        )}
      </div>
    </div>
  );
};

export default ExercisesPage;
