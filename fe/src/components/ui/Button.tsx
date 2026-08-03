import { forwardRef, type ComponentProps } from "react";
import { cn } from "~/utils/cn";

type ButtonVariant = "primary" | "secondary";

interface ButtonProps extends ComponentProps<"button"> {
  variant: ButtonVariant;
}

const variantStyle: Record<ButtonVariant, string> = {
  primary: "bg-blue-600 text-white hover:bg-blue-700",
  secondary: "bg-gray-600 text-white hover:bg-gray-700",
};

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, ...props }, ref) => {
    return (
      <button
        ref={ref}
        className={cn(
          "inline-flex items-center justify-center rounded-md px-3 py-2 font-medium cursor-pointer disabled:pointer-events-none disabled:opacity-50",
          variantStyle[variant],
          className,
        )}
        {...props}
      ></button>
    );
  },
);

Button.displayName = "Button";
