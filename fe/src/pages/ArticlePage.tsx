import { Link, useLocation, useParams } from "react-router-dom";
import { toast } from "sonner";
import { usePublicArticleBySlugQuery } from "~/api/articles.hooks";
import {
  usePurchaseCheckoutMutation,
  useSubscriptionCheckoutMutation,
} from "~/api/payments.hooks";
import { QueryView } from "~/components/QueryView";
import { Button } from "~/components/ui/button";
import { Spinner } from "~/components/ui/spinner";
import { useAuth } from "~/contexts/AuthContext";
import { useCustomSearchParams } from "~/hooks/useCustomSearchParams";
import type { PublicArticle } from "~/schemas/articles";
import {
  articlePageQuerySchema,
  type ArticlePageQuery,
  type LoginPageQuery,
} from "~/schemas/page";
import { PATHS } from "~/utils/paths";
import { buildPath } from "~/utils/url";

interface CallToActionProps {
  articleId: number;
  pastDueSubscription: boolean;
}

function CallToAction({ articleId, pastDueSubscription }: CallToActionProps) {
  const { user, authPending } = useAuth();
  const location = useLocation();
  const currentPath = location.pathname + location.search;
  const purchaseCheckoutMutation = usePurchaseCheckoutMutation();
  const subscriptionCheckoutMutation = useSubscriptionCheckoutMutation();

  if (authPending) {
    return null;
  }

  if (!user) {
    const loginPageQuery: LoginPageQuery = {
      redirect: currentPath,
    };
    const loginPagePath = buildPath(PATHS.LOGIN, loginPageQuery);

    return (
      <Link to={loginPagePath}>
        <Button variant="default">Login to read more</Button>
      </Link>
    );
  }

  if (pastDueSubscription) {
    return (
      <>
        <p className="text-amber-700">Your subscription is past due.</p>
        <Link to={PATHS.SETTINGS}>
          <Button variant="default">Manage billing</Button>
        </Link>
      </>
    );
  }

  const isPending =
    purchaseCheckoutMutation.isPending ||
    subscriptionCheckoutMutation.isPending;

  const articlePageQuery: ArticlePageQuery = {
    checkoutSuccess: true,
  };
  const redirectPath = buildPath(currentPath, articlePageQuery);

  const handlePurchase = async () => {
    try {
      await purchaseCheckoutMutation.mutateAsync({
        article_id: articleId,
        redirect_path: redirectPath,
      });
    } catch (err) {
      toast.error(`Error creating purchase checkout session: ${err}`);
    }
  };

  const handleSubscribe = async () => {
    try {
      await subscriptionCheckoutMutation.mutateAsync({
        redirect_path: redirectPath,
      });
    } catch (err) {
      toast.error(`Error creating subscription checkout session: ${err}`);
    }
  };

  return (
    <div className="flex items-center gap-2">
      <Button variant="default" disabled={isPending} onClick={handleSubscribe}>
        {subscriptionCheckoutMutation.isPending ? <Spinner /> : "Subscribe"}
      </Button>
      <span>or</span>
      <Button variant="default" disabled={isPending} onClick={handlePurchase}>
        {purchaseCheckoutMutation.isPending ? <Spinner /> : "Buy this article"}
      </Button>
    </div>
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
          {article.published_at
            ? `Published on ${new Date(article.published_at).toLocaleDateString()}`
            : "Draft / Retired"}
        </p>

        <div className="mb-6 prose text-gray-800 leading-relaxed">
          {article.content}
        </div>

        {article.access_status === "teaser" && (
          <div className="flex flex-col items-center gap-2">
            <h3 className="text-xl fold-bold">Continue reading</h3>
            <CallToAction
              articleId={article.id}
              pastDueSubscription={article.past_due_subscription}
            />
          </div>
        )}
      </div>
    </div>
  );
}

export default function ArticlePage() {
  const { slug } = useParams<{ slug: string }>();
  const { checkoutSuccess } = useCustomSearchParams(articlePageQuerySchema);
  const {
    data: article,
    isLoading,
    error,
  } = usePublicArticleBySlugQuery(slug, checkoutSuccess);

  return (
    <QueryView
      isLoading={isLoading}
      error={error}
      data={article}
      render={(article) => <ArticleDetails article={article} />}
    />
  );
}
