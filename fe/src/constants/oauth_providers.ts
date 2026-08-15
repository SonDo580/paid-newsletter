import type { OAuthProvider } from "~/schemas/auth";

interface ProviderMeta {
  id: OAuthProvider;
  name: string;
  // icon: ReactNode;
}

export const SUPPORTED_PROVIDERS: ProviderMeta[] = [
  {
    id: "google",
    name: "Google",
  },
];