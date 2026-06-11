// frontend/src/pages/NotFoundPage.tsx

import { Link } from "react-router-dom";
import { Button } from "@/components/ui/Button";

export default function NotFoundPage() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-surface-DEFAULT text-center">
      <h1 className="text-7xl font-bold text-brand-400">404</h1>
      <p className="mt-4 text-lg text-slate-400">Page not found</p>
      <Link to="/dashboard" className="mt-8">
        <Button>Back to Dashboard</Button>
      </Link>
    </div>
  );
}