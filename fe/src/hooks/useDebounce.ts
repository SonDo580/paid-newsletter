import { useEffect, useState } from "react";

export function useDebounce<T>(value: T, delay_ms: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedValue(value);
    }, delay_ms);

    return () => {
      clearTimeout(timer);
    };
  }, [value, delay_ms]);

  return debouncedValue;
}
