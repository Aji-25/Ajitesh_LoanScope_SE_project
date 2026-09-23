import type { InputHTMLAttributes, ReactNode, TextareaHTMLAttributes } from "react";

import { cn } from "@/lib/utils";

const fieldClass =
  "mt-2 w-full rounded-lg border border-white/10 bg-[#1f1f1f] px-3 py-2 text-base text-white placeholder:text-[#6f6f6f] transition-all duration-700 ease-[cubic-bezier(0.32,0.72,0,1)] hover:border-white/20 focus:border-[#d9ff76] focus:outline-none focus:ring-2 focus:ring-[#d9ff76]/20 disabled:cursor-not-allowed disabled:opacity-50";

type BaseFieldProps = {
  label: string;
  name: string;
  hint?: string;
  error?: string;
  children?: ReactNode;
};

export function FieldShell({ label, name, hint, error, children }: BaseFieldProps) {
  return (
    <div>
      <label className="text-sm font-semibold text-[#e5e5e5]" htmlFor={name}>
        {label}
      </label>
      {children}
      {error ? (
        <p className="mt-2 text-sm text-[#ff9b8f]" id={`${name}-error`}>
          {error}
        </p>
      ) : hint ? (
        <p className="mt-2 text-sm text-[#8f8f8f]" id={`${name}-hint`}>
          {hint}
        </p>
      ) : null}
    </div>
  );
}

type InputFieldProps = Omit<InputHTMLAttributes<HTMLInputElement>, "name"> & BaseFieldProps;

export function InputField({ label, name, hint, error, className, ...props }: InputFieldProps) {
  return (
    <FieldShell error={error} hint={hint} label={label} name={name}>
      <input
        aria-describedby={error ? `${name}-error` : hint ? `${name}-hint` : undefined}
        aria-invalid={Boolean(error)}
        className={cn(fieldClass, className)}
        id={name}
        name={name}
        {...props}
      />
    </FieldShell>
  );
}

type TextareaFieldProps = Omit<TextareaHTMLAttributes<HTMLTextAreaElement>, "name"> & BaseFieldProps;

export function TextareaField({
  label,
  name,
  hint,
  error,
  className,
  ...props
}: TextareaFieldProps) {
  return (
    <FieldShell error={error} hint={hint} label={label} name={name}>
      <textarea
        aria-describedby={error ? `${name}-error` : hint ? `${name}-hint` : undefined}
        aria-invalid={Boolean(error)}
        className={cn(fieldClass, "min-h-32 resize-y", className)}
        id={name}
        name={name}
        {...props}
      />
    </FieldShell>
  );
}
