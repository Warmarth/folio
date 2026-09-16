"use client";

import { useState, useEffect } from "react";

type Learner = { id: string; email?: string; role?: string };

export default function Learner() {
  const API_URL = process.env.NEXT_PUBLIC_API_URL;

  const [learners, setLearners] = useState<Learner[]>([]);

  useEffect(() => {
    const fetchLearners = async () => {
      const token = localStorage.getItem("access_token");

      if (!token) {
        console.log("No access token");
        return;
      }

      try {
        const response = await fetch(`${API_URL}/api/all_learner`, {
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        });

        if (!response.ok) {
          throw new Error("Failed to fetch learners");
        }

        const data = await response.json();

        console.log("Fetched learners:", data);

        setLearners(data.data || []);
      } catch (error) {
        console.error("Error fetching learners:", error);
      }
    };

    fetchLearners();
  }, [API_URL]);

  return (
    <div>
      <h1>Learners</h1>

      {learners.map((learner) => (
        <div
          key={learner.id}
          className="bg-white rounded-xl shadow-md p-5 border mb-3 w-96"
        >
          <div className="flex items-center gap-4">
            {/* Avatar */}
            <div className="w-12 h-12 rounded-full bg-blue-500 text-white flex items-center justify-center font-bold">
              {learner.email?.charAt(0).toUpperCase()}
            </div>

            {/* Learner information */}
            <div>
              <h3 className="font-semibold text-lg">{learner.email}</h3>

              <p className="text-sm text-gray-500">Role: {learner.role}</p>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
