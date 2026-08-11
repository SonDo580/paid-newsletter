import { useMutation } from "@tanstack/react-query";
import type {
  PurchaseCheckoutReqBody,
  SubscriptionCheckoutReqBody,
} from "~/schemas/payments";
import { purchaseCheckout, subscriptionCheckout } from "./payments";

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
