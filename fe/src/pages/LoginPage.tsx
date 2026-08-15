import { zodResolver } from "@hookform/resolvers/zod";
import { useState } from "react";
import { Controller, useForm } from "react-hook-form";
import { Navigate } from "react-router-dom";
import { getApiErrMsg } from "~/api/apiError";
import { useLoginMutation, useOAuthFlow } from "~/api/auth.hooks";
import { Button } from "~/components/ui/button";
import { Field, FieldError, FieldGroup } from "~/components/ui/field";
import { Input } from "~/components/ui/input";
import { Spinner } from "~/components/ui/spinner";
import { SUPPORTED_PROVIDERS } from "~/constants/oauth_providers";
import { useAuth } from "~/contexts/AuthContext";
import { useCustomSearchParams } from "~/hooks/useCustomSearchParams";
import { PATHS } from "~/paths";
import { loginSchema, type LoginFormValues } from "~/schemas/auth";
import { loginPageQuerySchema } from "~/schemas/page";

interface SocialLoginButtonsProps {
  redirectPath?: string;
}

function SocialLoginButtons({ redirectPath }: SocialLoginButtonsProps) {
  const { startOAuth, pendingProvider } = useOAuthFlow();

  return (
    <div className="space-y-3">
      {SUPPORTED_PROVIDERS.map((providerMeta) => {
        const isPending = pendingProvider === providerMeta.id;
        return (
          <Button
            key={providerMeta.id}
            variant="outline"
            disabled={Boolean(pendingProvider)}
            onClick={() =>
              startOAuth({
                provider: providerMeta.id,
                action: "login",
                redirectPath,
              })
            }
            className="flex items-center justify-center gap-2 w-full"
          >
            {isPending && <Spinner />}
            <span>Continue with {providerMeta.name}</span>
          </Button>
        );
      })}
    </div>
  );
}

interface EmailLoginFormProps {
  redirectPath?: string;
}

function EmailLoginForm({ redirectPath }: EmailLoginFormProps) {
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

  if (loginSuccess) {
    return (
      <div className="flex flex-col text-center">
        <h2 className="font-semibold text-lg">Check your email</h2>
        <p className="text-gray-600">
          We sent a login link to{" "}
          <span className="font-medium text-gray-900">
            {form.getValues("email")}
          </span>
        </p>
      </div>
    );
  }

  return (
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
              {fieldState.invalid && <FieldError errors={[fieldState.error]} />}
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
  );
}

export default function LoginPage() {
  const { user, authPending } = useAuth();
  const { redirect: redirectPath } =
    useCustomSearchParams(loginPageQuerySchema);

  if (authPending) {
    return null;
  }

  if (user) {
    return <Navigate to={redirectPath || PATHS.HOME} replace />;
  }

  return (
    <div className="flex justify-center p-4">
      <div className="w-full bg-white max-w-lg rounded-lg border border-gray-200 p-4 shadow-xs">
        <h1 className="text-center mb-6 text-2xl fond-bold">Log In</h1>
        <div className="space-y-6">
          <SocialLoginButtons redirectPath={redirectPath} />
          <div className="text-center text-sm text-blue-600">OR</div>
          <EmailLoginForm redirectPath={redirectPath} />
        </div>
      </div>
    </div>
  );
}
