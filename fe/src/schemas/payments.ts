export interface PurchaseCheckoutReqBody {
  article_id: number;
  redirect_path?: string;
}

export interface SubscriptionCheckoutReqBody {
  redirect_path?: string;
}

export interface CheckoutResBody {
  checkout_url: string;
}
