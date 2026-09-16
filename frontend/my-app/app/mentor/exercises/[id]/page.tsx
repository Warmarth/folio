'use client';

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";

const API_URL = process.env.NEXT_PUBLIC_API_URL;

type Exercise = {
  title?: string;
  description?: string;
  level?: string;
  category?: string;
  xp_points?: number;
  created_at?: string;
  instructions?: string;
  evaluation_criteria?: string;
};

export default function ExerciseDetailsPage() {
  const params = useParams();
  const id = params.id as string;

    const [exercise, setExercise] = useState<Exercise | null>(null);
    const [loading, setLoading] = useState(true); 

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
                            "Content-Type": "application/json",
                        },
                    }
                );

                if (!response.ok) {
                    throw new Error("Failed to fetch exercise");
                }

                const data = await response.json();
                setExercise(data.data || null);
            } catch (error) {
                console.error("Error fetching exercise:", error);
            } finally {
                setLoading(false);
            }
        }

        loadExercise();
    }, [id]);   

    return (
        <main className="p-8">
            {loading ? (
                <p>Loading exercise...</p>
            ) : exercise ? (
                <div>
                    <h1 className="text-2xl font-bold mb-4">{exercise.title}</h1>
                    <p className="mb-2"><strong>Description:</strong> {exercise.description}</p>
                    <p className="mb-2"><strong>Level:</strong> {exercise.level}</p>
                    <p className="mb-2"><strong>Category:</strong> {exercise.category}</p>
                    <p className="mb-2"><strong>XP Points:</strong> {exercise.xp_points}</p>
                    <p className="mb-2"><strong>Created At:</strong> {exercise.created_at ? new Date(exercise.created_at).toLocaleString() : "Not available"}</p>
                    <p className="mb-2"><strong>Instructions:</strong> {exercise.instructions}</p>
                    <p className="mb-2"><strong>Evaluation Criteria:</strong> {exercise.evaluation_criteria}</p>    
                </div>
            ) : (
                <p>Exercise not found.</p>  
            )}
        </main>
    );
}
