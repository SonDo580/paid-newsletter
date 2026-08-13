import type { ReactNode } from "react";
import { toast } from "sonner";
import { useCreateBillingPortalSessionMutation } from "~/api/payments.hooks";
import { Button } from "~/components/ui/button";
import { Spinner } from "~/components/ui/spinner";
import { useAuth } from "~/contexts/AuthContext";

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
          <div className="font-medium text-slate-500">
            Email: <span className="mt-0.5 text-slate-900">{user.email}</span>
          </div>
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
