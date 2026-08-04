import { zodResolver } from "@hookform/resolvers/zod";
import { useState } from "react";
import { FormState, useForm } from "react-hook-form";
import { Button } from "~/components/ui/Button";
import { Checkbox } from "~/components/ui/Checkbox";
import { FormField } from "~/components/ui/FormField";
import { Input } from "~/components/ui/Input";
import { Textarea } from "~/components/ui/Textarea";
import { articleFormSchema, type ArticleFormValues } from "~/schemas/articles";

interface ArticleFormProps {
  initialData?: ArticleFormValues;
  onSubmit: (
    data: ArticleFormValues,
    dirtyFields: FormState<ArticleFormValues>["dirtyFields"],
  ) => Promise<void> | void;
  isSubmitting: boolean;
  apiErrMsg: string;
}

export default function ArticleForm({
  initialData,
  onSubmit,
  isSubmitting,
  apiErrMsg,
}: ArticleFormProps) {
  const {
    register,
    handleSubmit,
    setValue,
    formState: { errors, isDirty, dirtyFields },
  } = useForm<ArticleFormValues>({
    resolver: zodResolver(articleFormSchema),
    defaultValues: {
      title: initialData?.title ?? "",
      slug: initialData?.slug ?? "",
      content: initialData?.content ?? "",
      is_free: initialData?.is_free ?? false,
      is_published: initialData?.is_published ?? false,
    },
  });

  const isEditMode = !!initialData;
  const [isSlugCustomized, setIsSlugCustomized] = useState(false);

  const handleTitleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (isEditMode || isSlugCustomized) {
      return;
    }
    const title = e.target.value;
    const generatedSlug = title
      .toLowerCase()
      .trim()
      .replace(/[^a-z0-9\s-]/g, "") // keep only letters, numbers, spaces, hyphens
      .replace(/[\s_-]+/g, "-") // collapse each run of spaces,underscores,hyphens into a hyphen
      .replace(/^-+|-+$/g, ""); // remove leading and trailing hyphens

    setValue("slug", generatedSlug, { shouldValidate: true });
  };

  const handleFormSubmit = (data: ArticleFormValues) => {
    onSubmit(data, dirtyFields);
  };

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">
        {isEditMode ? "Edit Article" : "Create Article"}
      </h1>

      <form
        onSubmit={handleSubmit(handleFormSubmit)}
        className="flex flex-col gap-4 max-w-2xl"
      >
        <FormField label="Title" error={errors.title?.message}>
          <Input
            type="text"
            placeholder="Title"
            {...register("title", {
              onChange: handleTitleChange,
            })}
          />
        </FormField>

        <FormField label="Slug" error={errors.slug?.message}>
          <Input
            type="text"
            placeholder="Slug"
            disabled={isEditMode}
            {...register("slug", {
              onChange: () => setIsSlugCustomized(true),
            })}
          />
        </FormField>

        <FormField label="Content" error={errors.content?.message}>
          <Textarea placeholder="Content" rows={5} {...register("content")} />
        </FormField>

        <div className="flex gap-6 p-2">
          <Checkbox label="Free" {...register("is_free")} />
          <Checkbox label="Publish" {...register("is_published")} />
        </div>

        <Button
          type="submit"
          variant="primary"
          disabled={isSubmitting || (!isDirty && isEditMode)}
        >
          {isSubmitting ? "Saving..." : "Save"}
        </Button>

        {apiErrMsg && <p className="text-red-700">{apiErrMsg}</p>}
      </form>
    </div>
  );
}
