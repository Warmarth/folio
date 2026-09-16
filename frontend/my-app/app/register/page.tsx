"use client";

import { FormEvent, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

export default function RegisterPage() {
  const router = useRouter();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState("learner");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const API_URL = process.env.NEXT_PUBLIC_API_URL;

  async function handleRegister(event: FormEvent<HTMLFormElement>) {
  event.preventDefault();

  console.log("API URL:", API_URL);

  setError("");
  setSuccess("");
  setLoading(true);

  try {

   const response = await fetch(`${API_URL}/auth/register`, {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    email: email.trim(),
    password,
    role,
  }),
});

    console.log("Status:", response.status);

    const data = await response.json();

    console.log("Backend response:", data);

    if (!response.ok) {
      setError(data.message || "Could not create account.");
      return;
    }

    setSuccess(data.message || "Account created successfully.");

    setTimeout(() => {
      router.push("/login");
    }, 1000);
  } catch (error) {
    console.error("Registration error:", error);

    setError(
      "Could not connect to the server. Make sure the backend is running."
    );
  } finally {
    setLoading(false);
  }
}
  return (
    <main className="min-h-screen bg-[#171613] px-5 py-8 text-[#f3efe3]">
      <div className="mx-auto grid min-h-[calc(100vh-4rem)] max-w-4xl overflow-hidden rounded-md border border-white/10 bg-[#201f1b] md:grid-cols-[0.85fr_1fr]">
        {/* Left side */}
        <section className="hidden flex-col justify-between border-r border-white/10 bg-[#171613] p-8 md:flex">
          <div>
            <Link
              href="/"
              className="font-serif text-4xl tracking-tight"
            >
              fol<span className="text-[#56a89b]">io</span>
            </Link>

            <p className="mt-2 font-mono text-[11px] tracking-widest text-white/40">
              LEARN · BUILD · PROVE
            </p>
          </div>

          <div>
            <p className="max-w-xs font-serif text-xl leading-relaxed text-white/85">
              A single place to build your skills, test what you know,
              and keep track of what you&apos;ve actually made.
            </p>
          </div>

          <div className="flex justify-between font-mono text-[10px] tracking-wider text-white/30">
            <span>FOLIO / 01</span>
            <span>CREATE</span>
          </div>
        </section>

        {/* Form */}
        <section className="bg-[#f3efe3] p-7 text-[#1f1b16] sm:p-10">
          <div className="mb-8">
            <Link
              href="/"
              className="font-serif text-3xl md:hidden"
            >
              fol<span className="text-[#56a89b]">io</span>
            </Link>

            <div className="mt-6 flex gap-6 border-b border-black/10">
              <Link
                href="/login"
                className="pb-3 font-mono text-xs uppercase tracking-wider text-black/40"
              >
                Sign in
              </Link>

              <span className="border-b-2 border-[#b5651d] pb-3 font-mono text-xs uppercase tracking-wider">
                Create account
              </span>
            </div>
          </div>

          <h1 className="font-serif text-3xl">
            Create your folio
          </h1>

          <p className="mt-2 text-sm text-black/50">
            Create your account and start testing what you know.
          </p>

          <form
            onSubmit={handleRegister}
            className="mt-8 flex flex-col gap-5"
          >
            <div>
              <label
                htmlFor="email"
                className="mb-2 block font-mono text-[10px] uppercase tracking-widest text-black/50"
              >
                Email
              </label>

              <input
                id="email"
                type="email"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                placeholder="you@example.com"
                required
                autoComplete="email"
                className="w-full rounded-sm border border-black/10 bg-[#fbfaf5] px-3 py-3 text-sm outline-none transition focus:border-[#3e7c74] focus:ring-2 focus:ring-[#3e7c74]/15"
              />
            </div>

            <div>
              <label
                htmlFor="password"
                className="mb-2 block font-mono text-[10px] uppercase tracking-widest text-black/50"
              >
                Password
              </label>

              <input
                id="password"
                type="password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                placeholder="••••••••"
                required
                minLength={8}
                autoComplete="new-password"
                className="w-full rounded-sm border border-black/10 bg-[#fbfaf5] px-3 py-3 text-sm outline-none transition focus:border-[#3e7c74] focus:ring-2 focus:ring-[#3e7c74]/15"
              />
            </div>

            <div>
              <label
                htmlFor="role"
                className="mb-2 block font-mono text-[10px] uppercase tracking-widest text-black/50"
              >
                Role
              </label>
              <select
                id="role"
                value={role}
                onChange={(event) => setRole(event.target.value)}
                className="w-full rounded-sm border border-black/10 bg-[#fbfaf5] px-3 py-3 text-sm outline-none transition focus:border-[#3e7c74] focus:ring-2 focus:ring-[#3e7c74]/15"
              >
                <option value="learner">Learner</option>
                <option value="mentor">Mentor</option>
              </select>
            </div>

            {error && (
              <div className="rounded-sm border border-[#c1553d]/20 bg-[#c1553d]/10 px-3 py-3 font-mono text-xs text-[#c1553d]">
                {error}
              </div>
            )}

            {success && (
              <div className="rounded-sm border border-[#3e7c74]/20 bg-[#3e7c74]/10 px-3 py-3 font-mono text-xs text-[#3e7c74]">
                {success}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="mt-2 rounded-sm bg-[#1f1b16] px-4 py-3 font-mono text-xs uppercase tracking-wider text-[#f3efe3] transition hover:bg-[#33291d] disabled:cursor-not-allowed disabled:opacity-50"
            >
              {loading ? "Creating account..." : "Create account"}
            </button>
          </form>

          <p className="mt-6 text-center text-xs text-black/50">
            Already have a folio?{" "}
            <Link
              href="/login"
              className="font-semibold text-[#b5651d] underline underline-offset-2"
            >
              Sign in
            </Link>
          </p>
        </section>
      </div>
    </main>
  );
}
