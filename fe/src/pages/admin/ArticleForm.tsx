import { useParams } from "react-router-dom";
import { Button } from "~/components/ui/Button";
import { Checkbox } from "~/components/ui/Checkbox";
import { Input } from "~/components/ui/Input";
import { Textarea } from "~/components/ui/Textarea";

export default function ArticleForm() {
  const { id } = useParams<{ id: string }>();

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">
        {id ? `Edit Article #${id}` : "Create Article"}
      </h1>
      <form className="flex flex-col gap-4 max-w-2xl">
        <Input type="text" placeholder="Title" />
        <Textarea placeholder="Content" rows={5} />
        <Input type="text" placeholder="Slug" />
        <div className="flex gap-6 p-2">
          <Checkbox label="Free" />
          <Checkbox label="Published" />
        </div>
        <Button type="button" variant="primary">
          {id ? "Update" : "Create"}
        </Button>
      </form>
    </div>
  );
}
