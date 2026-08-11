import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { getApiErrMsg } from "~/api/apiError";
import { useCreateArticleMutation } from "~/api/articles.hooks";
import type { ArticleFormValues } from "~/schemas/articles";
import { PATHS } from "~/paths";
import ArticleForm from "./ArticleForm";

export default function CreateArticlePage() {
  const navigate = useNavigate();
  const [createArticleErrMsg, setCreateArticleErrMsg] = useState<string>("");
  const { mutateAsync: createArticle, isPending: createArticlePending } =
    useCreateArticleMutation();

  const handleCreateArticle = async (data: ArticleFormValues) => {
    setCreateArticleErrMsg("");
    try {
      await createArticle(data);
      navigate(PATHS.ADMIN.ARTICLES);
    } catch (err) {
      setCreateArticleErrMsg(getApiErrMsg(err));
    }
  };

  return (
    <ArticleForm
      onSubmit={handleCreateArticle}
      isSubmitting={createArticlePending}
      apiErrMsg={createArticleErrMsg}
    />
  );
}
