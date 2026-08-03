import { Link } from "react-router-dom";
import { PATHS } from "~/constants/paths";

export default function Login() {
  return (
    <div className="flex justify-center p-4">
      <div className="w-full max-w-lg rounded-lg border border-gray-200 p-4 shadow-xs">
        <h1 className="text-center mb-6 text-2xl fond-bold">Log In</h1>
        <form className="flex flex-col gap-4">
          <input
            type="email"
            placeholder="Enter your email"
            className="w-full rounded-md border border-gray-300 p-2"
          />
          <button
            type="button"
            className="w-full rounded-lg py-2 bg-blue-600 text-white font-medium hover:bg-blue-700 cursor-pointer"
          >
            Send Login Link
          </button>
        </form>

        <div className="mt-4 text-center">
          <Link to={PATHS.HOME} className="text-gray-500 hover:underline">
            Return to Home
          </Link>
        </div>
      </div>
    </div>
  );
}
