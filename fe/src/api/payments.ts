import type {
  CheckoutResBody,
  PurchaseCheckoutReqBody,
  SubscriptionCheckoutReqBody,
} from "~/schemas/payments";
import { apiClient } from "./apiClient";

export async function purchaseCheckout(
  payload: PurchaseCheckoutReqBody,
): Promise<CheckoutResBody> {
  return apiClient<CheckoutResBody>("/checkout/purchase", {
    method: "POST",
    body: payload,
  });
}

export async function subscriptionCheckout(
  payload: SubscriptionCheckoutReqBody,
): Promise<CheckoutResBody> {
  return apiClient<CheckoutResBody>("/checkout/subscription", {
    method: "POST",
    body: payload,
  });
}
