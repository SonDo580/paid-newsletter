import type {
  CheckoutResBody,
  CreateBillingPortalSessionReqBody,
  CreateBillingPortalSessionResBody,
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


export async function createBillingPortalSession(
  payload: CreateBillingPortalSessionReqBody,
): Promise<CreateBillingPortalSessionResBody> {
  return apiClient<CreateBillingPortalSessionResBody>("/billing/portal", {
    method: "POST",
    body: payload,
  });
}

