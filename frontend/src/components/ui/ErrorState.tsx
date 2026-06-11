// frontend/src/components/ui/ErrorState.tsx

import { AlertCircle } from "lucide-react";

export function ErrorState({ message }: { message?: string }) {
  return (
    <div className="flex flex-col items-center justify-center py-20 text-center">
      <AlertCircle className="mb-3 h-10 w-10 text-red-400" />
      <p className="text-sm text-slate-400">{message ?? "Something went wrong. Please try again."}</p>
    </div>
  );
}