import { useMutation } from "@tanstack/react-query";
import type {
  CreateBillingPortalSessionReqBody,
  PurchaseCheckoutReqBody,
  SubscriptionCheckoutReqBody,
} from "~/schemas/payments";
import {
  createBillingPortalSession,
  purchaseCheckout,
  subscriptionCheckout,
} from "./payments";

export function usePurchaseCheckoutMutation() {
  return useMutation({
    mutationFn: (payload: PurchaseCheckoutReqBody) => purchaseCheckout(payload),
    onSuccess: (data) => {
      window.location.href = data.checkout_url;
    },
  });
}

export function useSubscriptionCheckoutMutation() {
  return useMutation({
    mutationFn: (payload: SubscriptionCheckoutReqBody) =>
      subscriptionCheckout(payload),
    onSuccess: (data) => {
      window.location.href = data.checkout_url;
    },
  });
}

export function useCreateBillingPortalSessionMutation() {
  return useMutation({
    mutationFn: (payload: CreateBillingPortalSessionReqBody) =>
      createBillingPortalSession(payload),
    onSuccess: (data) => {
      window.location.href = data.portal_url;
    },
  });
}
