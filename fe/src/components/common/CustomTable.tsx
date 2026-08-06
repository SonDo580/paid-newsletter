import type { ReactNode } from "react";
import { cn } from "~/lib/utils";
import type { SortOrder } from "~/schemas/shared";
import { Skeleton } from "../ui/skeleton";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "../ui/table";

export interface Column<T> {
  key: string;
  header: ReactNode;
  render?: (record: T) => ReactNode; // use 'record[key]' if not provide
  sortable?: boolean; // use 'key' as sort key
  sortKey?: string; // override sort key
  className?: string;
}

interface CustomTableProps<T> {
  columns: Column<T>[];
  data?: T[];
  error: Error | null;
  rowKey: (record: T) => string | number;
  isLoading?: boolean;
  emptyText?: string;
  sortBy?: string;
  sortOrder?: SortOrder;
  onSortChange?: (sortKey: string) => void;
  className?: string;
}

interface CustomTableHeadProps<T> {
  column: Column<T>;
  sortBy?: string;
  sortOrder?: SortOrder;
  onSortChange?: (sortKey: string) => void;
}

function CustomTableHead<T>({
  column,
  sortBy,
  sortOrder,
  onSortChange,
}: CustomTableHeadProps<T>) {
  const sortKey = column.sortKey ?? (column.sortable ? column.key : undefined);
  const isSortable = !!sortKey;
  const isSorted = isSortable && sortBy === sortKey;

  const handleClick = () => {
    if (sortKey && onSortChange) {
      onSortChange(sortKey);
    }
  };

  return (
    <TableHead
      key={column.key}
      className={cn(
        column.className,
        isSortable ? "cursor-pointer hover:bg-gray-100" : "",
      )}
      onClick={handleClick}
    >
      <div className="flex items-center gap-1">
        <span>{column.header}</span>
        {isSortable && (
          <span className="text-gray-400 text-xs">
            {isSorted ? (sortOrder === "asc" ? "▲" : "▼") : "↕"}
          </span>
        )}
      </div>
    </TableHead>
  );
}

interface CustomTableBodyProps<T> {
  columns: Column<T>[];
  data: T[];
  error?: Error | null;
  isLoading: boolean;
  emptyText: string;
  rowKey: (record: T) => string | number;
}

function CustomTableBody<T>({
  columns,
  data,
  error,
  isLoading,
  emptyText,
  rowKey,
}: CustomTableBodyProps<T>) {
  if (isLoading) {
    return (
      <TableBody>
        {Array.from({ length: 5 }).map((_, index) => (
          <TableRow key={index}>
            <TableCell colSpan={columns.length}>
              <Skeleton className="h-5 w-full" />
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    );
  }

  if (error) {
    return (
      <TableBody>
        <TableRow>
          <TableCell
            colSpan={columns.length}
            className="text-center py-8 text-red-600 text-lg"
          >
            {error.message}
          </TableCell>
        </TableRow>
      </TableBody>
    );
  }

  if (data.length === 0) {
    return (
      <TableBody>
        <TableRow>
          <TableCell
            colSpan={columns.length}
            className="text-center py-8 text-gray-500 text-lg"
          >
            {emptyText}
          </TableCell>
        </TableRow>
      </TableBody>
    );
  }

  return (
    <TableBody>
      {data.map((record) => (
        <TableRow key={rowKey(record)}>
          {columns.map((col) => (
            <TableCell key={col.key} className={col.className}>
              {col.render ? col.render(record) : record[col.key]}
            </TableCell>
          ))}
        </TableRow>
      ))}
    </TableBody>
  );
}

export function CustomTable<T>({
  columns,
  data = [],
  error,
  rowKey,
  isLoading = false,
  emptyText = "No data",
  sortBy,
  sortOrder,
  onSortChange,
  className = "",
}: CustomTableProps<T>) {
  return (
    <div className={cn("rounded-md border bg-card", className)}>
      <Table>
        <TableHeader>
          <TableRow>
            {columns.map((col) => (
              <CustomTableHead
                key={col.key}
                column={col}
                sortBy={sortBy}
                sortOrder={sortOrder}
                onSortChange={onSortChange}
              />
            ))}
          </TableRow>
        </TableHeader>

        <CustomTableBody
          columns={columns}
          data={data}
          error={error}
          isLoading={isLoading}
          emptyText={emptyText}
          rowKey={rowKey}
        />
      </Table>
    </div>
  );
}
