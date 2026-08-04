import { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { getApiErrMsg } from "~/api/apiError";
import {
  useArticleQuery,
  useUpdateArticleMutation,
} from "~/api/articles.hooks";
import type { Article, ArticleFormValues } from "~/schemas/articles";
import { PATHS } from "~/utils/paths";
import ArticleForm from "./ArticleForm";
import type { FormState } from "react-hook-form";
import { getDirtyValues } from "~/utils/form";

function articleToFormValues(article: Article): ArticleFormValues {
  return {
    title: article.title,
    slug: article.slug,
    content: article.content,
    is_free: article.is_free,
    is_published: article.is_published,
  };
}

export default function EditArticle() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [updateArticleErrMsg, setUpdateArticleErrMsg] = useState<string>("");
  const {
    data: article,
    isLoading: getArticleLoading,
    error: getArticleErr,
  } = useArticleQuery(id);
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

  if (getArticleLoading) {
    return <div>Loading article details...</div>;
  }

  if (getArticleErr) {
    return (
      <div className="text-read-600">
        Get article details error: {getArticleErr.message}
      </div>
    );
  }

  return (
    <ArticleForm
      initialData={articleToFormValues(article)}
      onSubmit={handleUpdateArticle}
      isSubmitting={updateArticlePending}
      apiErrMsg={updateArticleErrMsg}
    />
  );
}
