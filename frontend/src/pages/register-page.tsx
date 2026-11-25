import { ArrowLeft, UserPlus } from "@phosphor-icons/react";
import { useState, type FormEvent } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";

import { ApiError } from "@/api/client";
import { InputField } from "@/components/form-field";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/contexts/auth-store";

export function RegisterPage() {
  const { register, user } = useAuth();
  const navigate = useNavigate();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  if (user) return <Navigate replace to="/dashboard" />;

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    if (!email.includes("@")) {
      setError("Enter a valid email address.");
      return;
    }
    if (
      password.length < 12 ||
      !/[a-z]/.test(password) ||
      !/[A-Z]/.test(password) ||
      !/\d/.test(password)
    ) {
      setError("Use at least 12 characters with uppercase, lowercase, and a number.");
      return;
    }
    setSubmitting(true);
    try {
      await register(fullName, email, password);
      navigate("/dashboard", { replace: true });
    } catch (requestError) {
      setError(
        requestError instanceof ApiError
          ? requestError.message
          : "Registration could not be completed. Check the API connection and try again.",
      );
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="grid min-h-screen bg-[#131209] lg:grid-cols-2">
      <section className="hidden border-r border-white/10 bg-[#181818] p-12 lg:flex lg:flex-col lg:justify-between">
        <Link className="flex items-center gap-2 rounded-full font-semibold" to="/">
          <img src="/favicon.svg" alt="" className="size-8 shrink-0" />
          LoanScope
        </Link>
        <div className="max-w-xl">
          <p className="text-sm font-semibold text-[#d9ff76]">Accountable requirements</p>
          <h1 className="mt-4 text-balance text-5xl font-semibold">
            Create a workspace for decisions your delivery team can trace.
          </h1>
          <p className="mt-6 max-w-lg text-pretty text-lg text-[#9b9b9b]">
            Start with stakeholder evidence, preserve human review, and keep every generated artefact connected.
          </p>
        </div>
        <p className="text-sm text-[#6f6f6f]">Local course-project accounts use the Business Analyst role.</p>
      </section>
      <section className="grid place-items-center px-6 py-12">
        <div className="w-full max-w-md">
          <Link className="inline-flex items-center gap-2 rounded-md text-sm font-semibold text-[#9b9b9b] hover:text-white" to="/login">
            <ArrowLeft /> Back to sign in
          </Link>
          <span className="mt-10 grid size-12 place-items-center rounded-xl bg-[#272727] text-[#d9ff76]"><UserPlus size={24} /></span>
          <h2 className="mt-6 text-3xl font-semibold">Create your account</h2>
          <p className="mt-3 text-pretty text-[#9b9b9b]">Use a work email and a strong password for this local environment.</p>
          <form className="mt-8 space-y-5" noValidate onSubmit={handleSubmit}>
            <InputField autoComplete="name" disabled={submitting} label="Full name" name="fullName" onChange={(event) => setFullName(event.target.value)} required value={fullName} />
            <InputField autoComplete="email" disabled={submitting} label="Email address" name="email" onChange={(event) => setEmail(event.target.value)} required type="email" value={email} />
            <InputField autoComplete="new-password" disabled={submitting} label="Password" name="password" onChange={(event) => setPassword(event.target.value)} required type="password" value={password} />
            <p className="text-xs text-[#777]">At least 12 characters with uppercase, lowercase, and a number.</p>
            {error && <div className="rounded-lg border border-[#ff9b8f]/30 bg-[#ff9b8f]/10 p-3 text-sm text-[#ffb8af]" role="alert">{error}</div>}
            <Button className="w-full" disabled={submitting || !fullName || !email || !password} type="submit">
              {submitting ? "Creating account" : "Create account"}
            </Button>
          </form>
        </div>
      </section>
    </main>
  );
}
