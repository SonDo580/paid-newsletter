import { Link } from "react-router-dom";
import { usePublicArticlesInfiniteQuery } from "~/api/articles.hooks";
import { QueryView } from "~/components/QueryView";
import { Button } from "~/components/ui/button";
import { PATHS } from "~/utils/paths";

export default function HomePage() {
  const {
    data,
    isLoading,
    error,
    hasNextPage,
    fetchNextPage,
    isFetchingNextPage,
  } = usePublicArticlesInfiniteQuery();

  const articles = data?.pages.flatMap((page) => page.items);

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-4xl mx-auto rounded-lg border border-gray-200 p-6">
        <h1 className="text-2xl text-gray-600 font-semibold mb-2">
          Articles
        </h1>
        <QueryView
          isLoading={isLoading}
          error={error}
          data={articles}
          render={(articles) => (
            <>
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
            </>
          )}
        ></QueryView>
      </div>
    </div>
  );
}
