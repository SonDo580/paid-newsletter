import type { ReactNode } from "react";

interface QueryViewProps<T> {
  isLoading: boolean;
  error: Error | null;
  data?: T;
  render: (data: T) => ReactNode;
}

export function QueryView<T>({
  isLoading,
  error,
  data,
  render,
}: QueryViewProps<T>) {
  if (isLoading) {
    return <div>Loading...</div>;
  }
  if (error) {
    return <div className="text-red-600">{error.message}</div>;
  }
  if (!data) {
    return null;
  }
  return render(data);
}
