// frontend/src/pages/AuthCallbackPage.tsx

import { useEffect } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { useAuthStore } from "@/store/authStore";
import { PageSpinner } from "@/components/ui/Spinner";

export default function AuthCallbackPage() {
  const [params] = useSearchParams();
  const navigate = useNavigate();
  const { setTokens } = useAuthStore();

  useEffect(() => {
    const access = params.get("access_token");
    const refresh = params.get("refresh_token");

    if (access && refresh) {
      setTokens(access, refresh);
      navigate("/dashboard", { replace: true });
    } else {
      navigate("/", { replace: true });
    }
  }, []);

  return (
    <div className="flex min-h-screen items-center justify-center bg-surface-DEFAULT">
      <div className="text-center">
        <PageSpinner />
        <p className="mt-4 text-sm text-slate-500">Signing you in…</p>
      </div>
    </div>
  );
}