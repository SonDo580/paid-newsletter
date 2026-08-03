import { Link, useParams } from "react-router-dom";

export default function Article() {
  const { slug } = useParams<{ slug: string }>();

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="mx-auto max-w-4xl rounded-lg border border-gray-200 bg-white p-6 shadow-xs">
        <Link
          to="/"
          className="inline-block mb-6 text-xl text-blue-600 hover:underline"
        >
          Back to Home
        </Link>

        <h1 className="mb-4 text-3xl font-extrabold tracking-tight text-gray-900 capitalize">
          example title: {slug}
        </h1>

        <div className="text-gray-600 leading-relaxed">
          <p>
            Example content: Lorem ipsum dolor sit, amet consectetur adipisicing
            elit. Possimus harum facere, earum nobis ullam eveniet dicta
            quibusdam enim omnis cum delectus repellat distinctio ipsam animi
            nesciunt qui, recusandae dolor vel!
          </p>
        </div>
      </div>
    </div>
  );
}
