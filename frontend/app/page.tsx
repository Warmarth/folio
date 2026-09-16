"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

const REVIEWS = [
  {
    exercise: "Build a Flask route",
    line: 12,
    code: `@app.route("/exercises")
      def list_exercises():
    return db.query(Exercise).all()`,
    reviewer: "TF",
    name: "Reviewer · ex-Stripe",
    comment:
      "This will leak every field, including internal ones. Serialize explicitly before returning.",
  },
  {
    exercise: "Hash a password with bcrypt",
    line: 4,
    code: `password_hash = bcrypt.hashpw(
  pw, bcrypt.gensalt()
)`,
    reviewer: "MK",
    name: "Reviewer · backend @ fintech",
    comment:
      "Good instinct using gensalt() with no fixed rounds. Now compare it with checkpw on login.",
  },
  {
    exercise: "Design a JWT refresh flow",
    line: 21,
    code: `if not token_expired:
    return current_token`,
    reviewer: "RS",
    name: "Reviewer · platform engineering",
    comment:
      "Solid start. Talk this through in your 1:1 — refresh rotation is where most people get it wrong.",
  },
];

const FEATURES = [
  {
    title: "Hands-on projects",
    body: "Build practical projects that force you to apply programming concepts instead of simply following tutorials.",
  },
  {
    title: "Programming exercises",
    body: "Test your understanding of programming fundamentals with exercises designed to expose gaps in your knowledge.",
  },
  {
    title: "Technical questions",
    body: "Go beyond writing code. Test your understanding of the concepts, systems, and decisions behind the code.",
  },
  {
    title: "Code review",
    body: "Submit your work and receive meaningful feedback on code quality, architecture, security, performance, and best practices.",
  },
  {
    title: "AI-assisted evaluation",
    body: "Get an initial evaluation of your submission quickly while preparing your work for deeper human review.",
  },
  {
    title: "1:1 industry mentorship",
    body: "Talk directly with experienced professionals about your code, blockers, career questions, and real-world engineering.",
  },
];

const FLOW = [
  {
    step: "Create your profile",
    detail: "Tell Folio what you are learning and where you want to improve.",
  },
  {
    step: "Choose a challenge",
    detail: "Pick an exercise or hands-on project at the level you want to test.",
  },
  {
    step: "Build and submit",
    detail: "Solve the problem and submit your actual work.",
  },
  {
    step: "Get feedback",
    detail: "Receive evaluation and, where available, detailed code review.",
  },
  {
    step: "Learn from industry",
    detail: "Book a 1:1 session and talk through your work with a practitioner.",
  },
];

function ReviewPanel() {
  const [index, setIndex] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setIndex((current) => (current + 1) % REVIEWS.length);
    }, 3400);

    return () => clearInterval(timer);
  }, []);

  const review = REVIEWS[index];
  const codeLines = review.code.split("\n");

  return (
    <div
      className="w-full max-w-md overflow-hidden rounded-lg"
      style={{
        background: "#0F1F3D",
        boxShadow: "0 20px 40px -20px rgba(15,31,61,0.4)",
      }}
    >
      <div
        className="flex items-center justify-between px-4 py-3"
        style={{ borderBottom: "1px solid #223257" }}
      >
        <span
          className="text-[11px]"
          style={{
            color: "#64748B",
            fontFamily: "'IBM Plex Mono', monospace",
          }}
        >
          {review.exercise}
        </span>

        <span className="text-[11px]" style={{ color: "#3B4C74" }}>
          code review
        </span>
      </div>

      <div
        className="px-5 pt-5 font-mono text-[13px] leading-relaxed"
        style={{ minHeight: 96 }}
      >
        {codeLines.map((line, lineIndex) => (
          <div key={lineIndex} className="flex">
            <span
              className="w-6 shrink-0"
              style={{ color: "#3B4C74" }}
            >
              {review.line + lineIndex}
            </span>

            <span
              style={{
                color: lineIndex === 0 ? "#FFFFFF" : "#94A3B8",
              }}
            >
              {line}
            </span>
          </div>
        ))}
      </div>

      <div
        className="mx-5 my-4 flex gap-3 rounded-md px-4 py-3"
        style={{ background: "#16295A" }}
      >
        <div
          className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full text-[11px] font-semibold"
          style={{
            background: "#C9A227",
            color: "#0F1F3D",
          }}
        >
          {review.reviewer}
        </div>

        <div>
          <div
            className="mb-1 text-[11px]"
            style={{ color: "#94A3B8" }}
          >
            {review.name}
          </div>

          <div className="text-[13px]" style={{ color: "#FFFFFF" }}>
            {review.comment}
          </div>
        </div>
      </div>

      <div className="flex gap-1.5 px-5 pb-4">
        {REVIEWS.map((_, reviewIndex) => (
          <span
            key={reviewIndex}
            className="h-1 rounded-full transition-all"
            style={{
              width: reviewIndex === index ? 20 : 10,
              background:
                reviewIndex === index ? "#C9A227" : "#223257",
            }}
          />
        ))}
      </div>
    </div>
  );
}

export default function Home() {
  return (
    <main
      style={{
        background: "#FFFFFF",
        color: "#0F1F3D",
        fontFamily: "'IBM Plex Sans', sans-serif",
      }}
    >
      {/* Navigation */}
      <header
        className="flex items-center justify-between px-6 py-5 sm:px-10"
        style={{ borderBottom: "1px solid #E2E6ED" }}
      >
        <Link
          href="/"
          className="text-lg font-semibold tracking-tight"
          style={{ fontFamily: "'Space Grotesk', sans-serif" }}
        >
          folio
        </Link>

        <nav
          className="hidden items-center gap-8 text-sm md:flex"
          style={{ color: "#64748B" }}
        >
          <a href="#features">Features</a>
          <a href="#how-it-works">How it works</a>
          <a href="#mentorship">Mentorship</a>
        </nav>

        <div className="flex items-center gap-3">
          <Link
            href="/login"
            className="hidden rounded-md px-4 py-2 text-sm font-medium sm:block"
            style={{ color: "#0F1F3D" }}
          >
            Sign in
          </Link>

          <Link
            href="/register"
            className="rounded-md px-4 py-2 text-sm font-medium"
            style={{
              background: "#0F1F3D",
              color: "#FFFFFF",
            }}
          >
            Get started
          </Link>
        </div>
      </header>

      {/* Hero */}
      <section className="mx-auto flex max-w-7xl flex-col items-center gap-16 px-6 pb-20 pt-16 sm:px-10 lg:flex-row lg:pt-24">
        <div className="max-w-2xl flex-1">
          <div
            className="mb-5 inline-block rounded-full px-3 py-1 text-[11px] uppercase tracking-wide"
            style={{
              border: "1px solid #E2E6ED",
              color: "#64748B",
            }}
          >
            Hands-on learning · Code review · Industry mentorship
          </div>

          <h1
            className="mb-6 text-5xl leading-[1.05] sm:text-6xl"
            style={{
              fontFamily: "'Space Grotesk', sans-serif",
              fontWeight: 700,
            }}
          >
            Find the edge of
            <br />
            what you actually know.
          </h1>

          <p
            className="mb-8 max-w-xl text-base leading-7"
            style={{ color: "#64748B" }}
          >
            Folio is a practical learning platform where developers test
            their programming knowledge through real projects, exercises,
            technical questions, and code challenges — then get meaningful
            feedback from experienced engineers.
          </p>

          <div className="flex flex-wrap items-center gap-4">
            <Link
              href="/register"
              className="rounded-md px-5 py-3 text-sm font-medium"
              style={{
                background: "#0F1F3D",
                color: "#FFFFFF",
              }}
            >
              Start learning
            </Link>

            <a
              href="#how-it-works"
              className="text-sm font-medium"
              style={{ color: "#64748B" }}
            >
              See how Folio works →
            </a>
          </div>
        </div>

        <div className="flex-1">
          <ReviewPanel />
        </div>
      </section>

      {/* Stats */}
      <section
        className="px-6 py-6 sm:px-10"
        style={{
          borderTop: "1px solid #E2E6ED",
          borderBottom: "1px solid #E2E6ED",
          background: "#F7F8FA",
        }}
      >
        <div className="mx-auto flex max-w-7xl flex-wrap gap-x-12 gap-y-6">
          {[
            {
              value: "Projects",
              label: "Build practical experience",
            },
            {
              value: "Exercises",
              label: "Test your fundamentals",
            },
            {
              value: "Reviews",
              label: "Get meaningful feedback",
            },
            {
              value: "1:1",
              label: "Learn from practitioners",
            },
          ].map((stat) => (
            <div key={stat.value}>
              <div
                className="font-mono text-2xl"
                style={{ color: "#0F1F3D" }}
              >
                {stat.value}
              </div>

              <div
                className="text-[12px]"
                style={{ color: "#64748B" }}
              >
                {stat.label}
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Features */}
      <section
        id="features"
        className="mx-auto max-w-7xl px-6 py-20 sm:px-10"
      >
        <h2
          className="mb-2 text-2xl"
          style={{
            fontFamily: "'Space Grotesk', sans-serif",
            fontWeight: 700,
          }}
        >
          Built to test where you actually stand
        </h2>

        <p
          className="mb-10 max-w-2xl text-sm leading-6"
          style={{ color: "#64748B" }}
        >
          Not another platform where you simply consume courses.
          Folio gives you problems to solve, work to submit, and people
          who can challenge your thinking.
        </p>

        <div
          className="grid grid-cols-1 gap-px sm:grid-cols-2 lg:grid-cols-3"
          style={{ background: "#E2E6ED" }}
        >
          {FEATURES.map((feature) => (
            <div
              key={feature.title}
              className="p-6"
              style={{ background: "#FFFFFF" }}
            >
              <div className="mb-2 text-sm font-semibold">
                {feature.title}
              </div>

              <div
                className="text-[13px] leading-relaxed"
                style={{ color: "#64748B" }}
              >
                {feature.body}
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* How it works */}
      <section
        id="how-it-works"
        className="px-6 py-20 sm:px-10"
        style={{ background: "#0F1F3D" }}
      >
        <div className="mx-auto max-w-7xl">
          <h2
            className="mb-10 text-2xl"
            style={{
              fontFamily: "'Space Grotesk', sans-serif",
              fontWeight: 700,
              color: "#FFFFFF",
            }}
          >
            From learner to proven ability
          </h2>

          <div className="grid grid-cols-1 gap-10 md:grid-cols-5">
            {FLOW.map((item, index) => (
              <div key={item.step} className="relative">
                <div
                  className="mb-3 font-mono text-xs"
                  style={{ color: "#C9A227" }}
                >
                  {String(index + 1).padStart(2, "0")}
                </div>

                <div
                  className="mb-2 text-sm font-semibold"
                  style={{ color: "#FFFFFF" }}
                >
                  {item.step}
                </div>

                <div
                  className="text-[13px] leading-relaxed"
                  style={{ color: "#94A3B8" }}
                >
                  {item.detail}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Mentorship */}
      <section
        id="mentorship"
        className="mx-auto max-w-7xl px-6 py-20 sm:px-10"
      >
        <div
          className="rounded-xl p-8 sm:p-12"
          style={{
            background: "#F7F8FA",
            border: "1px solid #E2E6ED",
          }}
        >
          <div className="max-w-2xl">
            <div
              className="mb-3 font-mono text-xs uppercase tracking-wide"
              style={{ color: "#C9A227" }}
            >
              Industry connection
            </div>

            <h2
              className="mb-4 text-3xl"
              style={{
                fontFamily: "'Space Grotesk', sans-serif",
                fontWeight: 700,
              }}
            >
              Don&apos;t learn alone.
            </h2>

            <p
              className="mb-6 text-sm leading-7"
              style={{ color: "#64748B" }}
            >
              When you get stuck or want to understand how your work
              compares to professional standards, connect with people
              already working in the programming industry.
            </p>

            <Link
              href="/register"
              className="inline-block rounded-md px-5 py-3 text-sm font-medium"
              style={{
                background: "#0F1F3D",
                color: "#FFFFFF",
              }}
            >
              Join Folio
            </Link>
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="px-6 py-16 sm:px-10">
        <div className="mx-auto flex max-w-7xl flex-col items-start justify-between gap-6 sm:flex-row sm:items-center">
          <div>
            <div
              className="mb-1 text-xl"
              style={{
                fontFamily: "'Space Grotesk', sans-serif",
                fontWeight: 700,
              }}
            >
              Stop guessing what you know. Find out.
            </div>

            <div
              className="text-sm"
              style={{ color: "#64748B" }}
            >
              Build. Submit. Get reviewed. Improve.
            </div>
          </div>

          <Link
            href="/register"
            className="rounded-md px-5 py-3 text-sm font-medium"
            style={{
              background: "#0F1F3D",
              color: "#FFFFFF",
            }}
          >
            Create your profile
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer
        className="px-6 py-6 text-[12px] sm:px-10"
        style={{
          borderTop: "1px solid #E2E6ED",
          color: "#94A3B8",
        }}
      >
        <div className="mx-auto max-w-7xl">
          Folio · Hands-on learning · Code review · Industry mentorship
        </div>
      </footer>
    </main>
  );
}
