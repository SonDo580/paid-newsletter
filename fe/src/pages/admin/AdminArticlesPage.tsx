import { useState } from "react";
import { Link } from "react-router-dom";
import { useAdminArticlesQuery } from "~/api/articles.hooks";
import { CustomSelect } from "~/components/common/CustomSelect";
import { CustomTable, type Column } from "~/components/common/CustomTable";
import { Pagination } from "~/components/common/Pagination";
import { SearchInput } from "~/components/common/SearchInput";
import { Badge } from "~/components/ui/badge";
import { Button } from "~/components/ui/button";
import type {
  ArticlesListForAdminParams,
  ArticlesListItemForAdmin,
  ArticleSortBy,
} from "~/schemas/articles";
import type { SortOrder } from "~/schemas/shared";
import { PATHS } from "~/utils/paths";

const DEFAULT_PARAMS: ArticlesListForAdminParams = {
  page: 1,
  page_size: 10,
  keyword: "",
  is_free: undefined,
  is_published: undefined,
  sort_by: "id",
  sort_order: "desc",
};

export default function AdminArticlesPage() {
  const [params, setParams] =
    useState<ArticlesListForAdminParams>(DEFAULT_PARAMS);

  const updateParams = (newParams: Partial<ArticlesListForAdminParams>) => {
    setParams((prev) => ({ ...prev, ...newParams }));
  };

  const { data, isLoading, error } = useAdminArticlesQuery(params);

  const handleSort = (columnSortKey: string) => {
    const nextOrder: SortOrder =
      params.sort_by === columnSortKey && params.sort_order === "asc"
        ? "desc"
        : "asc";

    updateParams({
      sort_by: columnSortKey as ArticleSortBy,
      sort_order: nextOrder,
    });
  };

  const formatDate = (dateStr: string | null) =>
    dateStr
      ? new Date(dateStr).toLocaleDateString(undefined, {
          month: "short",
          day: "numeric",
          year: "numeric",
        })
      : "_";

  const tableColumns: Column<ArticlesListItemForAdmin>[] = [
    { key: "id", header: "ID", sortable: true },
    { key: "title", header: "Title", sortable: true },
    {
      key: "is_free",
      header: "Access type",
      render: (item) => (
        <Badge variant={item.is_free ? "outline" : "default"}>
          {item.is_free ? "Free" : "Paid"}
        </Badge>
      ),
    },
    {
      key: "is_published",
      header: "Publish status",
      render: (item) => (
        <Badge variant={item.is_published ? "outline" : "destructive"}>
          {item.is_published ? "Published" : "Private"}
        </Badge>
      ),
    },
    {
      key: "published_at",
      header: "Published at",
      sortable: true,
      render: (item) => formatDate(item.published_at),
    },
    {
      key: "created_at",
      header: "Created at",
      sortable: true,
      render: (item) => formatDate(item.created_at),
    },
    {
      key: "updated_at",
      header: "Updated at",
      sortable: true,
      render: (item) => formatDate(item.updated_at),
    },
    {
      key: "actions",
      header: "Actions",
      render: (item) => (
        <div className="flex items-center gap-2">
          <Link to={PATHS.ADMIN.EDIT_ARTICLE(item.id)}>
            <Button variant="default" size="sm">
              Edit
            </Button>
          </Link>
          <Link to={PATHS.ARTICLE(item.slug)} target="_blank">
            <Button variant="secondary" size="sm">
              Read
            </Button>
          </Link>
        </div>
      ),
    },
  ];

  return (
    <div className="space-y-4">
      <Link to={PATHS.ADMIN.CREATE_ARTICLE} className="inline-block">
        <Button variant="default">Create Article</Button>
      </Link>

      {/* Filter */}
      <div className="flex flex-wrap gap-3 p-4 bg-card border border-gray-200 rounded-lg shadow-xs">
        <SearchInput
          placeholder="Search"
          value={params.keyword ?? ""}
          onChange={(val) => updateParams({ keyword: val, page: 1 })}
          className="w-64"
        />

        <CustomSelect
          value={params.is_free === undefined ? "all" : String(params.is_free)}
          onValueChange={(val) =>
            updateParams({
              is_free: val === "all" ? undefined : val === "true",
              page: 1,
            })
          }
          options={[
            { value: "all", label: "All" },
            { value: "true", label: "Free" },
            { value: "false", label: "Paid" },
          ]}
          className="w-32"
        />

        <CustomSelect
          value={
            params.is_published === undefined
              ? "all"
              : String(params.is_published)
          }
          onValueChange={(val) =>
            updateParams({
              is_published: val === "all" ? undefined : val === "true",
              page: 1,
            })
          }
          options={[
            { value: "all", label: "All" },
            { value: "true", label: "Public" },
            { value: "false", label: "Private" },
          ]}
          className="w-32"
        />
      </div>

      {/* Table */}
      <CustomTable
        columns={tableColumns}
        data={data?.items}
        error={error}
        rowKey={(item) => item.id}
        isLoading={isLoading}
        sortBy={params.sort_by}
        sortOrder={params.sort_order}
        onSortChange={handleSort}
      />

      {/* Pagination */}
      <Pagination
        page={params.page ?? 1}
        pageSize={params.page_size ?? 10}
        totalItems={data?.total ?? 0}
        onPageChange={(page) => updateParams({ page })}
        onPageSizeChange={(page_size) => updateParams({ page_size })}
        pageSizeOptions={[1, 10, 20, 50]}
      />
    </div>
  );
}
