import type { HTMLAttributes, ButtonHTMLAttributes } from "react";
import { cn } from "../lib/utils";

export function Card({ className, ...props }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(
        "rounded-xl border border-white/10 bg-white/[0.045] shadow-panel backdrop-blur-xl",
        className,
      )}
      {...props}
    />
  );
}

export function Button({
  className,
  variant = "primary",
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & { variant?: "primary" | "ghost" }) {
  return (
    <button
      className={cn(
        "inline-flex items-center justify-center gap-2 rounded-lg px-4 py-2.5 text-sm font-bold transition duration-200 disabled:cursor-not-allowed disabled:opacity-60",
        variant === "primary"
          ? "bg-gradient-to-r from-cyan to-mint text-obsidian shadow-glow hover:-translate-y-0.5"
          : "border border-white/10 bg-white/[0.045] text-slate-100 hover:border-cyan/50 hover:bg-cyan/10",
        className,
      )}
      {...props}
    />
  );
}

export function Badge({ className, ...props }: HTMLAttributes<HTMLSpanElement>) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full border border-white/10 px-2.5 py-1 text-xs font-bold text-slate-400",
        className,
      )}
      {...props}
    />
  );
}
