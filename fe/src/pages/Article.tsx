import { Link, useParams } from "react-router-dom";
import { usePublicArticleBySlugQuery } from "~/api/articles.hooks";

export default function Article() {
  const { slug } = useParams<{ slug: string }>();
  const { data: article, isLoading, error } = usePublicArticleBySlugQuery(slug);

  if (isLoading) {
    return <div>Loading...</div>;
  }

  if (error) {
    return (
      <div className="text-read-600">Get article error: {error.message}</div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="mx-auto max-w-4xl rounded-lg border border-gray-200 bg-white p-6 shadow-xs">
        <Link
          to="/"
          className="inline-block mb-6 text-xl text-blue-600 hover:underline"
        >
          Back to Home
        </Link>

        <h1 className="mb-2 text-3xl font-extrabold tracking-tight text-gray-900 capitalize">
          {article.title}
        </h1>

        <p className="mb-6 text-sm text-gray-500">
          Published on {new Date(article.published_at).toLocaleDateString()}
        </p>

        <div className="mb-6 prose text-gray-800 leading-relaxed">
          {article.content}
        </div>

        {article.access_status == "teaser" && (
          <div>TODO (login + subscribe or pay)</div>
        )}
      </div>
    </div>
  );
}
