import { Link } from "react-router-dom";
import { Button } from "~/components/ui/Button";
import { PATHS } from "~/utils/paths";

export default function AdminArticles() {
  //   Mock data
  const articles = [
    {
      id: 0,
      title: "String String String String",
      slug: "string-string-string-string",
      is_free: true,
      is_published: true,
      created_at: "2026-08-03T04:03:19.124Z",
      updated_at: "2026-08-03T04:03:19.124Z",
      published_at: "2026-08-03T04:03:19.124Z",
    },
    {
      id: 1,
      title: "String String String String 1",
      slug: "string-string-string-string-1",
      is_free: false,
      is_published: false,
      created_at: "2026-08-03T04:03:19.124Z",
      updated_at: "2026-08-03T04:03:19.124Z",
      published_at: null,
    },
  ];

  const cellCls = "px-4 py-2";

  const formatDate = (dateStr: string | null) => {
    if (!dateStr) {
      return "_";
    }
    return new Date(dateStr).toLocaleDateString(undefined, {
      month: "short",
      day: "numeric",
      year: "numeric",
    });
  };

  return (
    <div className="rounded-lg border border-gray-200">
      <table className="w-full text-left">
        <thead className="bg-gray-50 font-semibold text-gray-700 border-b border-gray-200">
          <tr>
            <th className={cellCls}>ID</th>
            <th className={cellCls}>Title</th>
            <th className={cellCls}>Slug</th>
            <th className={cellCls}>Free</th>
            <th className={cellCls}>Published</th>
            <th className={cellCls}>Published at</th>
            <th className={cellCls}>Created at</th>
            <th className={cellCls}>Updated at</th>
            <th className={cellCls}>Actions</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-200 bg-white text-gray-700">
          {articles.map((a) => (
            <tr key={a.id}>
              <td className={cellCls}>{a.id}</td>
              <td className={cellCls}>{a.title}</td>
              <td className={cellCls}>{a.slug}</td>
              <td className={cellCls}>{a.is_free ? "Free" : "Paid"}</td>
              <td className={cellCls}>
                {a.is_published ? "Public" : "Private"}
              </td>
              <td className={cellCls}>{formatDate(a.published_at)}</td>
              <td className={cellCls}>{formatDate(a.created_at)}</td>
              <td className={cellCls}>{formatDate(a.updated_at)}</td>
              <td className={`${cellCls} flex gap-2`}>
                <Link to={PATHS.ADMIN.EDIT_ARTICLE(a.id)}>
                  <Button variant="primary">Edit</Button>
                </Link>
                <Link to={PATHS.ARTICLE(a.slug)} target="_blank">
                  <Button variant="secondary">Read</Button>
                </Link>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
