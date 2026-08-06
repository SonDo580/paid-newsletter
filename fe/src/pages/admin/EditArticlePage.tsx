import { useState } from "react";
import type { FormState } from "react-hook-form";
import { useNavigate, useParams } from "react-router-dom";
import { getApiErrMsg } from "~/api/apiError";
import {
  useArticleByIdQuery,
  useUpdateArticleMutation,
} from "~/api/articles.hooks";
import { QueryView } from "~/components/QueryView";
import type { Article, ArticleFormValues } from "~/schemas/articles";
import { getDirtyValues } from "~/utils/form";
import { PATHS } from "~/utils/paths";
import ArticleForm from "./ArticleForm";

function articleToFormValues(article: Article): ArticleFormValues {
  return {
    title: article.title,
    slug: article.slug,
    content: article.content,
    is_free: article.is_free,
    is_published: article.is_published,
  };
}

export default function EditArticlePage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [updateArticleErrMsg, setUpdateArticleErrMsg] = useState<string>("");
  const {
    data: article,
    isLoading: getArticleLoading,
    error: getArticleErr,
  } = useArticleByIdQuery(id);
  const { mutateAsync: updateArticle, isPending: updateArticlePending } =
    useUpdateArticleMutation(id);

  const handleUpdateArticle = async (
    data: ArticleFormValues,
    dirtyFields: FormState<ArticleFormValues>["dirtyFields"],
  ) => {
    setUpdateArticleErrMsg("");
    try {
      const updatePayload = getDirtyValues(dirtyFields, data);
      await updateArticle(updatePayload);
      navigate(PATHS.ADMIN.ARTICLES);
    } catch (err) {
      setUpdateArticleErrMsg(getApiErrMsg(err));
    }
  };

  return (
    <QueryView
      isLoading={getArticleLoading}
      error={getArticleErr}
      data={article}
      render={(article) => (
        <ArticleForm
          initialData={articleToFormValues(article)}
          onSubmit={handleUpdateArticle}
          isSubmitting={updateArticlePending}
          apiErrMsg={updateArticleErrMsg}
        />
      )}
    ></QueryView>
  );
}
