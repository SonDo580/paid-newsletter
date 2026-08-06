import { useEffect, useState, type ChangeEvent } from "react";
import { Button } from "../ui/button";
import { Input } from "../ui/input";
import { CustomSelect } from "./CustomSelect";

interface PaginationProps {
  page: number;
  pageSize: number;
  totalItems: number;
  onPageChange: (page: number) => void;
  onPageSizeChange: (pageSize: number) => void;
  pageSizeOptions?: number[];
}

interface PageJumperProps {
  page: number;
  totalPages: number;
  onPageChange: (page: number) => void;
}

function PageJumper({ page, totalPages, onPageChange }: PageJumperProps) {
  const [inputVal, setInputVal] = useState<string>(String(page));

  useEffect(() => {
    setInputVal(String(page));
  }, [page]);

  const commitPageChange = () => {
    const parsed = Number(inputVal);
    if (!isNaN(parsed) && parsed >= 1 && parsed <= totalPages) {
      onPageChange(parsed);
    } else {
      setInputVal(String(page)); // revert to current valid page
    }
  };

  const handleInputChange = (e: ChangeEvent<HTMLInputElement>) => {
    setInputVal(e.target.value);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      e.currentTarget.blur();
    }
  };

  return (
    <div>
      <Input
        type="number"
        min={1}
        max={totalPages}
        value={inputVal}
        onChange={handleInputChange}
        onKeyDown={handleKeyDown}
        onBlur={commitPageChange}
        className="w-16 h-8"
      />
      <span> / {totalPages}</span>
    </div>
  );
}

export function Pagination({
  page,
  pageSize,
  totalItems,
  onPageChange,
  onPageSizeChange,
  pageSizeOptions = [10, 20, 50],
}: PaginationProps) {
  const totalPages = Math.ceil(totalItems / pageSize);
  if (totalPages === 0) {
    return null;
  }

  return (
    <div className="flex items-center justify-end gap-4 py-2">
      <div className="flex items-center gap-2">
        <span>Page Size</span>
        <CustomSelect
          value={String(pageSize)}
          onValueChange={(val) => {
            onPageSizeChange(Number(val));
            onPageChange(1);
          }}
          options={pageSizeOptions.map((size) => ({
            value: String(size),
            label: String(size),
          }))}
          className="w-16"
        />
      </div>

      <div className="flex items-center gap-2">
        <Button
          variant="outline"
          disabled={page == 1}
          onClick={() => onPageChange(page - 1)}
        >
          {"<"}
        </Button>

        <PageJumper
          page={page}
          totalPages={totalPages}
          onPageChange={onPageChange}
        />

        <Button
          variant="outline"
          disabled={page == totalPages}
          onClick={() => onPageChange(page + 1)}
        >
          {">"}
        </Button>
      </div>
    </div>
  );
}
