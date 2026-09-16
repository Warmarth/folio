"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";

export default function CreateExerciseForm() {
  const router = useRouter();

  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [category, setCategory] = useState("");
  const [difficulty, setDifficulty] = useState("beginner");
  const [instructions, setInstructions] = useState("");
  const [evaluationCriteria, setEvaluationCriteria] = useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const API_URL = process.env.NEXT_PUBLIC_API_URL;

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    setError("");
    setSuccess("");
    setLoading(true);

    const token = localStorage.getItem("access_token");

    if (!token) {
      setError("You must be logged in as a mentor.");
      setLoading(false);
      return;
    }
    const pattern = `${description.trim()} ${category} ${instructions.trim()} ${evaluationCriteria.trim()}`;
    try {
      const response = await fetch(
        `${API_URL}/api/exercises/create_exercise`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            title: title.trim(),
            description: pattern,
            level: difficulty,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        setError(data.message || "Failed to create exercise.");
        return;
      }

      setSuccess(data.message || "Exercise created successfully.");

      setTimeout(() => {
        router.push("/mentor/exercises");
      }, 1000);
    } catch (error) {
      console.error(error);
      setError("Could not connect to the server.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-3xl">
      {/* Header */}
      <div className="mb-8">
        <p className="text-sm text-gray-500">Exercises</p>

        <h1 className="mt-1 text-3xl font-bold">
          Create Exercise
        </h1>

        <p className="mt-2 text-gray-500">
          Create a practical exercise for your learners.
        </p>
      </div>

      {/* Form */}
      <form
        onSubmit={handleSubmit}
        className="space-y-6 rounded-2xl border bg-white p-6 shadow-sm"
      >
        {/* Title */}
        <div>
          <label className="mb-2 block text-sm font-medium">
            Exercise Title
          </label>

          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="e.g. Build a REST API"
            required
            className="w-full rounded-lg border px-4 py-3 outline-none transition focus:border-black"
          />
        </div>

        {/* Description */}
        <div>
          <label className="mb-2 block text-sm font-medium">
            Description
          </label>

          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Briefly explain what this exercise is about..."
            rows={4}
            required
            className="w-full resize-none rounded-lg border px-4 py-3 outline-none transition focus:border-black"
          />
        </div>

        {/* Category + Difficulty */}
        <div className="grid gap-5 md:grid-cols-2">
          <div>
            <label className="mb-2 block text-sm font-medium">
              Category
            </label>

            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              required
              className="w-full rounded-lg border bg-white px-4 py-3 outline-none focus:border-black"
            >
              <option value="">Select category</option>
              <option value="programming">Programming</option>
              <option value="frontend">Frontend</option>
              <option value="backend">Backend</option>
              <option value="database">Database</option>
              <option value="design">Design</option>
              <option value="business">Business</option>
              <option value="other">Other</option>
            </select>
          </div>

          <div>
            <label className="mb-2 block text-sm font-medium">
              Difficulty
            </label>

            <select
              value={difficulty}
              onChange={(e) => setDifficulty(e.target.value)}
              className="w-full rounded-lg border bg-white px-4 py-3 outline-none focus:border-black"
            >
              <option value="easy">easy</option>
              <option value="medium">medium</option>
              <option value="hard">hard</option>
              <option value="expert">expert</option>
              <option value="possible">Possible</option>
            </select>
          </div>
        </div>

        {/* Instructions */}
        <div>
          <label className="mb-2 block text-sm font-medium">
            Instructions
          </label>

          <textarea
            value={instructions}
            onChange={(e) => setInstructions(e.target.value)}
            placeholder="Tell the learner exactly what they need to do..."
            rows={7}
            required
            className="w-full resize-none rounded-lg border px-4 py-3 outline-none focus:border-black"
          />
        </div>

        {/* Evaluation Criteria */}
        <div>
          <label className="mb-2 block text-sm font-medium">
            Evaluation Criteria
          </label>

          <textarea
            value={evaluationCriteria}
            onChange={(e) => setEvaluationCriteria(e.target.value)}
            placeholder="What should the AI look for when evaluating the learner's answer?"
            rows={5}
            className="w-full resize-none rounded-lg border px-4 py-3 outline-none focus:border-black"
          />

          <p className="mt-2 text-xs text-gray-500">
            These criteria can be used by Folio&apos;s AI evaluator when
            scoring submissions.
          </p>
        </div>

        {/* Messages */}
        {error && (
          <div className="rounded-lg bg-red-50 px-4 py-3 text-sm text-red-600">
            {error}
          </div>
        )}

        {success && (
          <div className="rounded-lg bg-green-50 px-4 py-3 text-sm text-green-600">
            {success}
          </div>
        )}

        {/* Actions */}
        <div className="flex justify-end gap-3 border-t pt-5">
          <button
            type="button"
            onClick={() => router.back()}
            className="rounded-lg border px-5 py-2.5 text-sm font-medium hover:bg-gray-50"
          >
            Cancel
          </button>

          <button
            type="submit"
            disabled={loading}
            className="rounded-lg bg-black px-5 py-2.5 text-sm font-medium text-white hover:bg-gray-800 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {loading ? "Creating..." : "Create Exercise"}
          </button>
        </div>
      </form>
    </div>
  );
}

