import { useEffect, useState } from "react";
import { useDebounce } from "~/hooks/useDebounce";
import { Input } from "../ui/input";

interface SearchInputProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  delay_ms?: number;
  className?: string;
}

export function SearchInput({
  value,
  onChange,
  placeholder,
  delay_ms = 300,
  className,
}: SearchInputProps) {
  const [text, setText] = useState(value);
  const debouncedText = useDebounce(text, delay_ms);

  useEffect(() => {
    setText(value);
  }, [value]);

  useEffect(() => {
    if (debouncedText !== value) {
      onChange(debouncedText);
    }
  }, [debouncedText]);

  return (
    <Input
      type="text"
      placeholder={placeholder}
      value={text}
      onChange={(e) => setText(e.target.value)}
      className={className}
    />
  );
}
