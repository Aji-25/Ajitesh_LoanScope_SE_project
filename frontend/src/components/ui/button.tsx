import { Slot } from "@radix-ui/react-slot";
import { cva, type VariantProps } from "class-variance-authority";
import type { ButtonHTMLAttributes } from "react";

import { cn } from "@/lib/utils";

const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 rounded-lg px-3 py-2 text-base font-semibold transition-all duration-700 ease-[cubic-bezier(0.32,0.72,0,1)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#d9ff76] focus-visible:ring-offset-2 focus-visible:ring-offset-[#131209] disabled:pointer-events-none disabled:opacity-50 active:scale-[0.98]",
  {
    variants: {
      variant: {
        primary: "bg-[#d9ff76] text-[#131209] hover:bg-[#edffb7] hover:-translate-y-0.5",
        secondary:
          "border border-[#313131] bg-[#1f1f1f] text-white hover:border-[#5d5d5d] hover:bg-[#272727]",
        ghost: "text-[#c8c8c8] hover:bg-[#272727] hover:text-white",
      },
      size: {
        default: "h-11",
        small: "h-9 text-sm",
      },
    },
    defaultVariants: {
      variant: "primary",
      size: "default",
    },
  },
);

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> &
  VariantProps<typeof buttonVariants> & {
    asChild?: boolean;
  };

function Button({ className, variant, size, asChild = false, ...props }: ButtonProps) {
  const Component = asChild ? Slot : "button";
  return <Component className={cn(buttonVariants({ variant, size }), className)} {...props} />;
}

export { Button };
