import { ArrowLeft, LockKey } from "@phosphor-icons/react";
import { useState, type FormEvent } from "react";
import { Link, Navigate, useLocation, useNavigate } from "react-router-dom";

import { ApiError } from "@/api/client";
import { InputField } from "@/components/form-field";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/contexts/auth-store";

export function LoginPage() {
  const { login, user } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
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
    setSubmitting(true);
    try {
      await login(email, password);
      const destination = (location.state as { from?: { pathname?: string } } | null)?.from?.pathname;
      navigate(destination ?? "/dashboard", { replace: true });
    } catch (requestError) {
      setError(
        requestError instanceof ApiError
          ? requestError.message
          : "Login could not be completed. Check the API connection and try again.",
      );
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="grid min-h-screen bg-[#131209] lg:grid-cols-2">
      <section className="hidden border-r border-white/10 bg-[#181818] p-12 lg:flex lg:flex-col lg:justify-between">
        <Link className="flex items-center gap-2 rounded-full font-semibold" to="/">
          <span className="grid size-8 place-items-center rounded-full bg-[#d9ff76] text-sm font-bold text-[#131209]">C</span>
          Clarifi
        </Link>
        <div className="max-w-xl">
          <p className="text-sm font-semibold text-[#d9ff76]">Controlled discovery</p>
          <h1 className="mt-4 text-balance text-5xl font-semibold">
            Keep every lending requirement connected to its source.
          </h1>
          <p className="mt-6 max-w-lg text-pretty text-lg text-[#9b9b9b]">
            Review project context, stakeholder input, approvals, and delivery decisions in one traceable workspace.
          </p>
        </div>
        <p className="text-sm text-[#6f6f6f]">Requirement engineering for personal loan software projects</p>
      </section>
      <section className="grid place-items-center px-6 py-16">
        <div className="w-full max-w-md">
          <Link className="inline-flex items-center gap-2 rounded-md text-sm font-semibold text-[#9b9b9b] hover:text-white lg:hidden" to="/">
            <ArrowLeft aria-hidden="true" /> Back to overview
          </Link>
          <span className="mt-12 grid size-12 place-items-center rounded-xl bg-[#272727] text-[#d9ff76] lg:mt-0">
            <LockKey aria-hidden="true" size={24} />
          </span>
          <h2 className="mt-6 text-3xl font-semibold">Sign in to your workspace</h2>
          <p className="mt-3 text-pretty text-base text-[#9b9b9b]">
            Use the local analyst account configured for this environment.
          </p>
          <form className="mt-8 space-y-6" noValidate onSubmit={handleSubmit}>
            <InputField
              autoComplete="email"
              disabled={submitting}
              label="Email address"
              name="email"
              onChange={(event) => setEmail(event.target.value)}
              placeholder="name@company.com"
              required
              type="email"
              value={email}
            />
            <InputField
              autoComplete="current-password"
              disabled={submitting}
              label="Password"
              name="password"
              onChange={(event) => setPassword(event.target.value)}
              required
              type="password"
              value={password}
            />
            {error && (
              <div className="rounded-lg border border-[#ff9b8f]/30 bg-[#ff9b8f]/10 p-3 text-sm text-[#ffb8af]" role="alert">
                {error}
              </div>
            )}
            <Button className="w-full" disabled={submitting || !email || !password} type="submit">
              {submitting ? "Signing in" : "Sign in"}
            </Button>
          </form>
          <p className="mt-6 text-center text-sm text-[#9b9b9b]">
            New to Clarifi?{" "}
            <Link
              className="rounded font-semibold text-[#d9ff76] outline-none hover:text-white focus:ring-2 focus:ring-[#d9ff76]"
              to="/register"
            >
              Create an account
            </Link>
          </p>
        </div>
      </section>
    </main>
  );
}
