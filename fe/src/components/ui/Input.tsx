import { forwardRef, type ComponentProps } from "react";
import { cn } from "~/utils/cn";

export const inputCls =
  "w-full rounded-md border border-gray-300 p-2 text-gray-900 placeholder:text-gray-500 focus:border-blue-500 focus:outline-hidden focus:ring-1 focus:ring-blue-500 disabled:opacity-50 disabled:bg-gray-50";

export const Input = forwardRef<HTMLInputElement, ComponentProps<"input">>(
  ({ className, type, ...props }, ref) => {
    return (
      <input
        ref={ref}
        type={type}
        className={cn(inputCls, className)}
        {...props}
      />
    );
  },
);

Input.displayName = "Input";
