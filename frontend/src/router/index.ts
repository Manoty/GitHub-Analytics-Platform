// frontend/src/router/index.tsx

import { createBrowserRouter } from "react-router-dom";
import { AppLayout } from "@/components/layout/AppLayout";
import { ProtectedRoute } from "./ProtectedRoute";
import LandingPage from "@/pages/LandingPage";
import AuthCallbackPage from "@/pages/AuthCallbackPage";
import DashboardPage from "@/pages/DashboardPage";
import RepositoriesPage from "@/pages/RepositoriesPage";
import RepositoryDetailPage from "@/pages/RepositoryDetailPage";
import ContributorsPage from "@/pages/ContributorsPage";
import HealthPage from "@/pages/HealthPage";
import ComparePage from "@/pages/ComparePage";
import NotFoundPage from "@/pages/NotFoundPage";

export const router = createBrowserRouter([
  { path: "/",               element: <LandingPage /> },
  { path: "/auth/callback",  element: <AuthCallbackPage /> },
  {
    element: (
      <ProtectedRoute>
        <AppLayout />
      </ProtectedRoute>
    ),
    children: [
      { path: "/dashboard",           element: <DashboardPage /> },
      { path: "/repositories",        element: <RepositoriesPage /> },
      { path: "/repositories/:id",    element: <RepositoryDetailPage /> },
      { path: "/contributors",        element: <ContributorsPage /> },
      { path: "/health",              element: <HealthPage /> },
      { path: "/compare",             element: <ComparePage /> },
    ],
  },
  { path: "*", element: <NotFoundPage /> },
]);