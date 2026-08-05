import { zodResolver } from "@hookform/resolvers/zod";
import { useState } from "react";
import { Controller, FormState, useForm } from "react-hook-form";
import { Button } from "~/components/ui/button";
import { Checkbox } from "~/components/ui/checkbox";
import {
  Field,
  FieldError,
  FieldGroup,
  FieldLabel,
} from "~/components/ui/field";
import { Input } from "~/components/ui/input";
import { Textarea } from "~/components/ui/textarea";
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
  const isEditMode = !!initialData;
  const [isSlugCustomized, setIsSlugCustomized] = useState(false);

  const form = useForm<ArticleFormValues>({
    resolver: zodResolver(articleFormSchema),
    defaultValues: initialData || {
      title: "",
      slug: "",
      content: "",
      is_free: false,
      is_published: false,
    },
  });

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

    form.setValue("slug", generatedSlug, { shouldValidate: true });
  };

  const handleFormSubmit = (data: ArticleFormValues) => {
    onSubmit(data, form.formState.dirtyFields);
  };

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">
        {isEditMode ? "Edit Article" : "Create Article"}
      </h1>

      <form
        onSubmit={form.handleSubmit(handleFormSubmit)}
        className="flex flex-col gap-4 max-w-2xl"
      >
        <FieldGroup>
          <Controller
            name="title"
            control={form.control}
            render={({ field, fieldState }) => (
              <Field>
                <FieldLabel>Title</FieldLabel>
                <Input
                  {...field}
                  placeholder="Title"
                  onChange={(e) => {
                    field.onChange(e);
                    handleTitleChange(e);
                  }}
                />
                {fieldState.invalid && (
                  <FieldError errors={[fieldState.error]} />
                )}
              </Field>
            )}
          />

          <Controller
            name="slug"
            control={form.control}
            render={({ field, fieldState }) => (
              <Field>
                <FieldLabel>Slug</FieldLabel>
                <Input
                  {...field}
                  placeholder="Slug"
                  disabled={isEditMode}
                  onChange={(e) => {
                    field.onChange(e);
                    setIsSlugCustomized(true);
                  }}
                />
                {fieldState.invalid && (
                  <FieldError errors={[fieldState.error]} />
                )}
              </Field>
            )}
          />

          <Controller
            name="content"
            control={form.control}
            render={({ field, fieldState }) => (
              <Field>
                <FieldLabel>Content</FieldLabel>
                <Textarea {...field} placeholder="Content" rows={5} />
                {fieldState.invalid && (
                  <FieldError errors={[fieldState.error]} />
                )}
              </Field>
            )}
          />

          <Controller
            name="is_free"
            control={form.control}
            render={({ field }) => (
              <Field className="flex items-center gap-2">
                <FieldLabel className="cursor-pointer">
                  <Checkbox
                    checked={!!field.value}
                    onCheckedChange={field.onChange}
                  />
                  Free
                </FieldLabel>
              </Field>
            )}
          />

          <Controller
            name="is_published"
            control={form.control}
            render={({ field }) => (
              <Field className="flex items-center gap-2">
                <FieldLabel className="cursor-pointer">
                  <Checkbox
                    checked={!!field.value}
                    onCheckedChange={field.onChange}
                  />
                  Publish
                </FieldLabel>
              </Field>
            )}
          />
        </FieldGroup>

        <Button
          type="submit"
          variant="default"
          disabled={isSubmitting || (!form.formState.isDirty && isEditMode)}
        >
          {isSubmitting ? "Saving..." : "Save"}
        </Button>

        {apiErrMsg && <p className="text-red-700">{apiErrMsg}</p>}
      </form>
    </div>
  );
}
