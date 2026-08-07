import { Link, useLocation, useParams } from "react-router-dom";
import { usePublicArticleBySlugQuery } from "~/api/articles.hooks";
import { QueryView } from "~/components/QueryView";
import { Button } from "~/components/ui/button";
import { useAuth } from "~/contexts/AuthContext";
import type { PublicArticle } from "~/schemas/articles";
import { PATHS } from "~/utils/paths";

function CallToAction() {
  const { user, authPending } = useAuth();
  const location = useLocation();
  const currentPath = encodeURIComponent(location.pathname + location.search);
  const loginPath = `${PATHS.LOGIN}?redirect=${currentPath}`;

  if (authPending) {
    return null;
  }

  if (!user) {
    return (
      <Link to={loginPath}>
        <Button variant="default">Login to read more</Button>
      </Link>
    );
  }

  return (
    <div>TODO: pending subscription payment OR need to purchase/subscribe</div>
  );
}

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

        {article.access_status === "teaser" && <CallToAction />}
      </div>
    </div>
  );
}

export default function ArticlePage() {
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
