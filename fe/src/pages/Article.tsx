import { useParams } from "react-router-dom";
import { usePublicArticleBySlugQuery } from "~/api/articles.hooks";
import { QueryView } from "~/components/QueryView";
import type { PublicArticle } from "~/schemas/articles";

interface ArticleDetailsProps {
  article: PublicArticle;
}

function ArticleDetails({ article }: ArticleDetailsProps) {
  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="mx-auto max-w-4xl rounded-lg border border-gray-200 bg-white p-6 shadow-xs">
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

export default function Article() {
  const { slug } = useParams<{ slug: string }>();
  const { data: article, isLoading, error } = usePublicArticleBySlugQuery(slug);

  return (
    <QueryView
      isLoading={isLoading}
      error={error}
      data={article}
      render={(article) => <ArticleDetails article={article} />}
    />
  );
}
