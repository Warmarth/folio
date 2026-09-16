"use client";

import { FormEvent, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

export default function LoginPage() {
  const router = useRouter();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const API_URL = process.env.NEXT_PUBLIC_API_URL;

async function handleLogin(event: FormEvent<HTMLFormElement>) {
  event.preventDefault();

  setLoading(true);

  try {
    const response = await fetch(`${API_URL}/auth/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        email,
        password,
      }),
    });

    console.log("Status:", response.status);

    const data = await response.json();

    // console.log("Backend response:", data);

    if (!response.ok) {
      setError(data.message || "Login failed");
      return;
    }

    localStorage.setItem("access_token", data.access_token);
    localStorage.setItem("role", data.role);
    if (data.role !== "mentor") {
      router.push("/me");
    }else {
      router.push("/mentor");
    }
  } catch (error) {
    console.error("LOGIN ERROR:", error);
    setError("Could not connect to the server.");
  }finally{
    setLoading(false)
  }
}

  return (
    <main className="min-h-screen bg-[#171613] px-5 py-8 text-[#f3efe3]">
      <div className="mx-auto grid min-h-[calc(100vh-4rem)] max-w-4xl overflow-hidden rounded-md border border-white/10 bg-[#201f1b] md:grid-cols-[0.85fr_1fr]">
        
        {/* Left panel */}
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

          <p className="max-w-xs font-serif text-xl leading-relaxed text-white/85">
            A single place to keep what you&apos;ve made, test what you know,
            and grow as a developer.
          </p>

          <div className="flex justify-between font-mono text-[10px] tracking-wider text-white/30">
            <span>FOLIO / 01</span>
            <span>SIGN IN</span>
          </div>
        </section>

        {/* Login panel */}
        <section className="bg-[#f3efe3] p-7 text-[#1f1b16] sm:p-10">
          
          {/* Mobile logo */}
          <Link
            href="/"
            className="font-serif text-3xl md:hidden"
          >
            fol<span className="text-[#56a89b]">io</span>
          </Link>

          {/* Tabs */}
          <div className="mt-6 flex gap-6 border-b border-black/10">
            <span className="border-b-2 border-[#b5651d] pb-3 font-mono text-xs uppercase tracking-wider">
              Sign in
            </span>

            <Link
              href="/register"
              className="pb-3 font-mono text-xs uppercase tracking-wider text-black/40"
            >
              Create account
            </Link>
          </div>

          <div className="mt-8">
            <h1 className="font-serif text-3xl">
              Welcome back
            </h1>

            <p className="mt-2 text-sm text-black/50">
              Sign in to continue working on your folio.
            </p>
          </div>

          <form
            onSubmit={handleLogin}
            className="mt-8 flex flex-col gap-5"
          >
            {/* Email */}
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

            {/* Password */}
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
                autoComplete="current-password"
                className="w-full rounded-sm border border-black/10 bg-[#fbfaf5] px-3 py-3 text-sm outline-none transition focus:border-[#3e7c74] focus:ring-2 focus:ring-[#3e7c74]/15"
              />
            </div>

            {/* Error */}
            {error && (
              <div className="rounded-sm border border-[#c1553d]/20 bg-[#c1553d]/10 px-3 py-3 font-mono text-xs text-[#c1553d]">
                {error}
              </div>
            )}

            {/* Submit */}
            <button
              type="submit"
              disabled={loading}
              className="mt-2 rounded-sm bg-[#1f1b16] px-4 py-3 font-mono text-xs uppercase tracking-wider text-[#f3efe3] transition hover:bg-[#33291d] disabled:cursor-not-allowed disabled:opacity-50"
            >
              {loading ? "Signing in..." : "Sign in"}
            </button>
          </form>

          <p className="mt-6 text-center text-xs text-black/50">
            New to Folio?{" "}
            <Link
              href="/register"
              className="font-semibold text-[#b5651d] underline underline-offset-2"
            >
              Create your folio
            </Link>
          </p>
        </section>
      </div>
    </main>
  );
}
