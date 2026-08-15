import { useState, type ReactNode } from "react";
import { toast } from "sonner";
import { API_BASE_URL } from "~/api/apiClient";
import { useCreateBillingPortalSessionMutation } from "~/api/payments.hooks";
import { Button } from "~/components/ui/button";
import { Spinner } from "~/components/ui/spinner";
import { useAuth } from "~/contexts/AuthContext";
import type {
  OAuthAccount,
  OAuthAuthorizeParams,
  OAuthProvider,
} from "~/schemas/auth";
import { buildUrl } from "~/utils/url";

interface AccountSectionProps {
  title: string;
  description?: string;
  children: ReactNode;
}

function AccountSection({ title, description, children }: AccountSectionProps) {
  return (
    <section className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
      <h2 className="text-lg font-semibold text-slate-900">{title}</h2>
      {description && (
        <p className="mt-1 text-sm text-slate-500">{description}</p>
      )}
      <div className="mt-4">{children}</div>
    </section>
  );
}

interface ProviderMeta {
  id: OAuthProvider;
  name: string;
  // icon: ReactNode;
}

const SUPPORTED_PROVIDERS: ProviderMeta[] = [
  {
    id: "google",
    name: "Google",
  },
];

interface ConnectedAccountsProps {
  connectedAccounts: OAuthAccount[];
}

function ConnectedAccounts({ connectedAccounts }: ConnectedAccountsProps) {
  const [connectingProvider, setConnectingProvider] =
    useState<OAuthProvider | null>(null);

  const handleConnectProvider = async (provider: OAuthProvider) => {
    setConnectingProvider(provider);
    const currentPath = window.location.pathname;
    const params: OAuthAuthorizeParams = {
      action: "connect",
      redirect_path: currentPath,
    };
    const authorizeUrl = buildUrl(
      API_BASE_URL,
      `/auth/${provider}/authorize`,
      params,
    );
    window.location.href = authorizeUrl;
  };

  return SUPPORTED_PROVIDERS.map((provider_meta) => {
    const connectedAccount = connectedAccounts.find(
      (acc) => acc.provider === provider_meta.id,
    );
    const isConnecting = connectingProvider === provider_meta.id;

    return (
      <div key={provider_meta.id} className="flex items-center justify-between">
        <span className="font-medium text-slate-900">
          {provider_meta.name}:
        </span>
        <span className="text-slate-600">
          {connectedAccount ? (
            `Connected as ${connectedAccount.identifier}`
          ) : (
            <Button
              variant="default"
              disabled={Boolean(connectingProvider)}
              onClick={() => handleConnectProvider(provider_meta.id)}
            >
              {isConnecting ? <Spinner /> : "Connect"}
            </Button>
          )}
        </span>
      </div>
    );
  });
}

export default function AccountPage() {
  const { user, authPending } = useAuth();
  const billingPortalSessionMutation = useCreateBillingPortalSessionMutation();

  if (authPending) {
    return (
      <div className="flex items-center justify-center">
        <Spinner />
      </div>
    );
  }

  if (!user) {
    return null;
  }

  const hasStripeProfile = Boolean(user.reader?.has_stripe_profile);

  const handleManageBilling = async () => {
    const currentPath = window.location.pathname;
    try {
      await billingPortalSessionMutation.mutateAsync({
        redirect_path: currentPath,
      });
    } catch (err) {
      toast.error(`Error creating billing portal session: ${err}`);
    }
  };

  return (
    <div className="mx-auto max-w-2xl space-y-8 p-6">
      {/* Account Information */}
      <AccountSection title="Account Information">
        <div className="space-y-3 text-sm">
          <div className="flex items-center justify-between">
            <span className="font-medium text-slate-900">Email:</span>
            <span className="text-slate-600">{user.email}</span>
          </div>
          {user.reader && (
            <ConnectedAccounts connectedAccounts={user.reader.oauth_accounts} />
          )}
        </div>
      </AccountSection>

      {/* Billing Settings */}
      {hasStripeProfile && (
        <AccountSection
          title="Billing Settings"
          description="View your invoice history, payment receipts, or update payment details."
        >
          <Button
            variant="default"
            disabled={billingPortalSessionMutation.isPending}
            onClick={handleManageBilling}
          >
            {billingPortalSessionMutation.isPending ? (
              <Spinner />
            ) : (
              "Manage billing"
            )}
          </Button>
        </AccountSection>
      )}
    </div>
  );
}
