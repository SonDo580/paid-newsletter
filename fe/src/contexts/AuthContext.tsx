import React, { type ReactNode } from "react";
import { useCurrentUserQuery } from "~/api/auth.hooks";
import type { CurrentUser } from "~/schemas/auth";

interface AuthContextType {
  user: CurrentUser | null;
  authPending: boolean;
}

const AuthContext = React.createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const { data: user = null, isLoading: authPending } = useCurrentUserQuery();
  const contextValue = {
    user,
    authPending,
  };

  return (
    <AuthContext.Provider value={contextValue}>{children}</AuthContext.Provider>
  );
}

export function useAuth(): AuthContextType {
  const contextValue = React.useContext(AuthContext);
  if (!contextValue) {
    throw new Error("useAuth must be used withing an AuthProvider");
  }
  return contextValue;
}
