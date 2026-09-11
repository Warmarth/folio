"use client";

import { useState, useEffect } from "react";

export default function Learner() {
  const API_URL = process.env.NEXT_PUBLIC_API_URL;

  const [learners, setLearners] = useState<any[]>([]);

  useEffect(() => {
    const fetchLearners = async () => {
      const token = localStorage.getItem("access_token");

      if (!token) {
        console.log("No access token");
        return;
      }

      try {
        const response = await fetch(
          `${API_URL}/api/all_learner`,
          {
            headers: {
              Authorization: `Bearer ${token}`,
              "Content-Type": "application/json",
            },
          }
        );

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
        <div key={learner.id}>
          <p>{learner.email}</p>
          <p>{learner.role}</p>
        </div>
      ))}
    </div>
  );
}