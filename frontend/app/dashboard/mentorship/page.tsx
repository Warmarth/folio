"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

interface MentorProfile {
  id: string;
  name?: string;
  bio?: string;
  expertise?: string;
  image?: string;
}

export default function MentorshipPage() {
  const router = useRouter();

  const [profiles, setProfiles] = useState<MentorProfile[]>([]);
  const [loading, setLoading] = useState(true);

  const API_URL = process.env.NEXT_PUBLIC_API_URL;

  useEffect(() => {
    const fetchProfiles = async () => {
      try {
        const token = localStorage.getItem("access_token");

        if (!token) {
          console.log("No access token");
          return;
        }

        const response = await fetch(`${API_URL}/api/all_mentors`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.message || "Failed to fetch mentors");
        }

        console.log("Mentors:", data.data);

        setProfiles(data.data);
      } catch (error) {
        console.error("Error fetching mentors:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchProfiles();
  }, [API_URL]);

  if (loading) {
    return (
      <main className="p-8">
        <h1 className="mb-4 text-2xl font-bold">Mentorship</h1>
        <p>Loading mentors...</p>
      </main>
    );
  }

  return (
    <>
      <div className="mx-auto max-w-6xl">
        <h1 className="mb-2 text-2xl font-bold">Find a Mentor</h1>

        <p className="mb-6 text-gray-500">
          Choose a mentor and start learning.
        </p>

        {profiles.length > 0 ? (
          <div className="grid grid-cols-1 gap-5 md:grid-cols-2 lg:grid-cols-3">
            {profiles.map((profile) => (
              <div
                key={profile.id}
                onClick={() =>
                  router.push(`/dashboard/mentorship/${profile.id}`)
                }
                className="cursor-pointer rounded-xl border bg-white p-5 transition hover:-translate-y-1 hover:shadow-md"
              >
                {/* Image */}
                {profile.image ? (
                  <img
                    src={profile.image}
                    alt={profile.name || "Mentor"}
                    className="mb-4 h-40 w-full rounded-lg object-cover"
                  />
                ) : (
                  <div className="mb-4 flex h-40 items-center justify-center rounded-lg bg-gray-100 text-4xl font-bold">
                    {profile.name?.charAt(0).toUpperCase() || "M"}
                  </div>
                )}

                <h2 className="text-xl font-bold">
                  {profile.name || "Unnamed Mentor"}
                </h2>

                <p className="mt-2 line-clamp-2 text-sm text-gray-600">
                  {profile.bio || "No bio available."}
                </p>

                <p className="mt-3 text-sm">
                  <span className="font-semibold">Expertise:</span>{" "}
                  {profile.expertise || "Not specified"}
                </p>

                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    router.push(`/dashboard/mentorship/${profile.id}`);
                  }}
                  className="mt-5 w-full rounded-lg bg-black px-4 py-2.5 text-sm font-medium text-white hover:bg-gray-800"
                >
                  View Mentor
                </button>
              </div>
            ))}
          </div>
        ) : (
          <div className="rounded-xl border bg-white p-8 text-center">
            <p className="text-gray-500">No mentors available.</p>
          </div>
        )}
      </div>
    </>
  );
}