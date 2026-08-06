import { type ReactNode } from "react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../ui/select";

export interface SelectOption<V extends string> {
  value: V;
  label: ReactNode;
  disabled?: boolean;
}

interface CustomSelectProps<V extends string> {
  value?: V;
  onValueChange?: (value: V) => void;
  options: SelectOption<V>[];
  placeholder?: string;
  className?: string;
  disabled?: boolean;
}

export function CustomSelect<V extends string>({
  value,
  onValueChange,
  options,
  placeholder,
  className,
  disabled,
}: CustomSelectProps<V>) {
  return (
    <Select
      items={options}
      value={value}
      onValueChange={onValueChange}
      disabled={disabled}
    >
      <SelectTrigger className={className}>
        <SelectValue placeholder={placeholder} />
      </SelectTrigger>
      <SelectContent>
        {options.map((o) => (
          <SelectItem key={o.value} value={o.value} disabled={o.disabled}>
            {o.label}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}
