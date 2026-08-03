import { forwardRef, type ComponentProps } from "react";
import { cn } from "~/utils/cn";
import { inputCls } from "./Input";

export const Textarea = forwardRef<
  HTMLTextAreaElement,
  ComponentProps<"textarea">
>(({ className, ...props }, ref) => {
  return <textarea ref={ref} className={cn(inputCls, className)} {...props} />;
});

Textarea.displayName = "Textarea";
