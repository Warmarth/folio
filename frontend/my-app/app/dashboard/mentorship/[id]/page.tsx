"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";

interface Mentor {
  name?: string;
  email?: string;
  image?: string;
  bio?: string;
  expertise?: string;
}

export default function MentorshipDetailsPage() {
  const params = useParams();
  const mentor_id = params.id as string;

  const [mentor, setMentor] = useState<Mentor>({});
  const [loading, setLoading] = useState(true);

  const API_URL = process.env.NEXT_PUBLIC_API_URL;

  useEffect(() => {
    const fetchMentor = async () => {
      try {
        const token = localStorage.getItem("access_token");

        if (!token) {
          console.log("No access token");
          return;
        }

        console.log("Fetching mentor with ID:", mentor_id);

        const response = await fetch(
          `${API_URL}/api/all_mentors/${mentor_id}`,
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          },
        );

        const data = await response.json();

        console.log("Fetched mentor data:", data);

        if (!response.ok) {
          throw new Error(data.message || "Failed to fetch mentor");
        }

        setMentor(data.data);
      } catch (error) {
        console.error("Error fetching mentor:", error);
      } finally {
        setLoading(false);
      }
    };

    if (mentor_id) {
      fetchMentor();
    }
  }, [mentor_id, API_URL]);

  if (loading) {
    return (
      <main className="p-8">
        <p>Loading mentor...</p>
      </main>
    );
  }

  return (
    <>
      <div className="mx-auto max-w-3xl">
        <h1 className="mb-6 text-2xl font-bold">Mentor Profile</h1>

        {mentor.name ? (
          <div className="overflow-hidden rounded-2xl border bg-white shadow-sm">
            {mentor.image && (
              <img
                src={mentor.image}
                alt={mentor.name}
                className="h-64 w-full object-cover"
              />
            )}

            <div className="p-6">
              <h2 className="text-2xl font-bold">{mentor.name}</h2>

              {mentor.email && (
                <p className="mt-1 text-gray-500">{mentor.email}</p>
              )}

              {mentor.bio && (
                <div className="mt-6">
                  <h3 className="font-semibold">About</h3>
                  <p className="mt-2 text-gray-600">{mentor.bio}</p>
                </div>
              )}

              {mentor.expertise && (
                <div className="mt-6">
                  <h3 className="font-semibold">Expertise</h3>
                  <p className="mt-2 text-gray-600">{mentor.expertise}</p>
                </div>
              )}

              <button className="mt-8 rounded-lg bg-black px-5 py-3 font-medium text-white hover:bg-gray-800">
                Start Mentorship
              </button>
            </div>
          </div>
        ) : (
          <div className="rounded-xl border bg-white p-6">
            <p>Mentor not found.</p>
          </div>
        )}
      </div>
    </>
  );
}
