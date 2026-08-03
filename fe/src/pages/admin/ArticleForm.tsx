import { useParams } from "react-router-dom";

export default function ArticleForm() {
  const { id } = useParams<{ id: string }>();

  const inputCls = "w-full rounded-md border border-gray-300 p-2";

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">
        {id ? `Edit Article #${id}` : "Create Article"}
      </h1>
      <form className="flex flex-col gap-4 max-w-2xl">
        <input type="text" placeholder="Title" className={inputCls} />
        <textarea
          placeholder="Content"
          rows={5}
          className={inputCls}
        ></textarea>
        <input type="text" placeholder="Slug" className={inputCls} />
        {/* is_free */}
        {/* is_published */}
        <button
          type="button"
          className="rounded-md bg-blue-600 p-2 text-white font-medium hover:bg-blue-700 cursor-pointer"
        >
          {id ? "Update" : "Create"}
        </button>
      </form>
    </div>
  );
}
