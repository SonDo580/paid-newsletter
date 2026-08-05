import { Link } from "react-router-dom";
import { usePublicArticlesInfiniteQuery } from "~/api/articles.hooks";
import { QueryView } from "~/components/common/QueryView";
import { Button } from "~/components/ui/Button";
import { PATHS } from "~/utils/paths";

export default function Home() {
  const {
    data,
    isLoading,
    error,
    hasNextPage,
    fetchNextPage,
    isFetchingNextPage,
  } = usePublicArticlesInfiniteQuery();

  const articles = data?.pages.flatMap((page) => page.items) ?? [];

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-4xl mx-auto rounded-lg border border-gray-200 p-6">
        <div className="flex items-center justify-between p-2 border-b border-gray-200 mb-6">
          <h1 className="text-2xl fold-bold text-gray-900">Articles</h1>
          <Link
            to={PATHS.LOGIN}
            className="text-xl text-blue-600 hover:underline"
          >
            Login
          </Link>
        </div>

        <QueryView isLoading={isLoading} error={error}>
          <ul>
            {articles.map((a) => (
              <li key={a.slug} className="py-2">
                <Link
                  to={PATHS.ARTICLE(a.slug)}
                  className="text-lg text-blue-600 hover:underline"
                >
                  {a.title}
                </Link>
              </li>
            ))}
          </ul>

          {hasNextPage && (
            <Button
              variant="secondary"
              onClick={() => fetchNextPage()}
              disabled={isFetchingNextPage}
            >
              {isFetchingNextPage ? "Loading more..." : "Load more"}
            </Button>
          )}
        </QueryView>
      </div>
    </div>
  );
}
