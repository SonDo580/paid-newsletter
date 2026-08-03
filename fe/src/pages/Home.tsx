import { Link } from "react-router-dom";
import { PATHS } from "~/constants/paths";

export default function Home() {
  const articles = [
    { title: "example title 1", slug: "example-slug-1" },
    { title: "example title 2", slug: "example-slug-2" },
    { title: "example title 3", slug: "example-slug-3" },
  ];

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-4xl mx-auto rounded-lg border border-gray-200 p-6">
        <div className="flex items-center justify-between p-2 border-b border-gray-200 mb-6">
          <h1 className="text-2xl fold-bold text-gray-900">Articles</h1>
          <Link
            to={PATHS.LOGIN}
            className="text-xl text-blue-600 hover:underline"
          >
            Login
          </Link>
        </div>

        <ul>
          {articles.map((a) => (
            <li key={a.slug} className="py-2">
              <Link
                to={PATHS.ARTICLE(a.slug)}
                className="text-lg text-blue-600 hover:underline"
              >
                {a.title}
              </Link>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
