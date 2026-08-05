import { Link } from "react-router-dom";
import { Button } from "~/components/ui/button";
import { Input } from "~/components/ui/input";
import { PATHS } from "~/utils/paths";

export default function Login() {
  return (
    <div className="flex justify-center p-4">
      <div className="w-full max-w-lg rounded-lg border border-gray-200 p-4 shadow-xs">
        <h1 className="text-center mb-6 text-2xl fond-bold">Log In</h1>
        <form className="flex flex-col gap-4">
          <Input type="email" placeholder="Enter your email" />
          <Button type="submit" variant="default">
            Send Login Link
          </Button>
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
