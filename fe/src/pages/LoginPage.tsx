import { zodResolver } from "@hookform/resolvers/zod";
import { useState } from "react";
import { Controller, useForm } from "react-hook-form";
import { Navigate } from "react-router-dom";
import { getApiErrMsg } from "~/api/apiError";
import { useLoginMutation } from "~/api/auth.hooks";
import { Button } from "~/components/ui/button";
import { Field, FieldError, FieldGroup } from "~/components/ui/field";
import { Input } from "~/components/ui/input";
import { useAuth } from "~/contexts/AuthContext";
import { useCustomSearchParams } from "~/hooks/useCustomSearchParams";
import { PATHS } from "~/paths";
import { loginSchema, type LoginFormValues } from "~/schemas/auth";
import { loginPageQuerySchema } from "~/schemas/page";

export default function LoginPage() {
  const { user, authPending } = useAuth();
  const { redirect: redirectPath } =
    useCustomSearchParams(loginPageQuerySchema);
  const [loginSuccess, setLoginSuccess] = useState<boolean>(false);
  const [loginErrMsg, setLoginErrMsg] = useState<string>("");
  const { mutateAsync: login, isPending: loginPending } = useLoginMutation();

  const form = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
    mode: "onBlur",
    defaultValues: {
      email: "",
    },
  });

  const handleLogin = async (data: LoginFormValues) => {
    setLoginErrMsg("");
    try {
      await login({ email: data.email, redirect_path: redirectPath });
      setLoginSuccess(true);
    } catch (err) {
      setLoginErrMsg(getApiErrMsg(err));
    }
  };

  if (authPending) {
    return null;
  }

  if (user) {
    return <Navigate to={redirectPath || PATHS.HOME} replace />;
  }

  return (
    <div className="flex justify-center p-4">
      <div className="w-full max-w-lg rounded-lg border border-gray-200 p-4 shadow-xs">
        <h1 className="text-center mb-6 text-2xl fond-bold">Log In</h1>

        {loginSuccess ? (
          <div className="flex flex-col text-center">
            <h2 className="font-semibold text-lg">Check your email</h2>
            <p className="text-gray-600">
              We sent a login link to{" "}
              <span className="font-medium text-gray-900">
                {form.getValues("email")}
              </span>
            </p>
          </div>
        ) : (
          <form
            onSubmit={form.handleSubmit(handleLogin)}
            className="flex flex-col gap-4"
          >
            <FieldGroup>
              <Controller
                name="email"
                control={form.control}
                render={({ field, fieldState }) => (
                  <Field>
                    <Input
                      {...field}
                      type="email"
                      placeholder="Email"
                      autoComplete="email"
                    />
                    {fieldState.invalid && (
                      <FieldError errors={[fieldState.error]} />
                    )}
                  </Field>
                )}
              />
            </FieldGroup>

            <Button
              type="submit"
              variant="default"
              disabled={loginPending || !form.formState.isDirty}
            >
              {loginPending ? "Sending Link..." : "Send Login Link"}
            </Button>

            {loginErrMsg && <p className="text-red-700">{loginErrMsg}</p>}
          </form>
        )}
      </div>
    </div>
  );
}
