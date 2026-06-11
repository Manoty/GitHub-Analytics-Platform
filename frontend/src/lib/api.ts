// frontend/src/lib/api.ts

import axios from "axios";

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "/api/v1";

export const api = axios.create({
  baseURL: BASE_URL,
  headers: { "Content-Type": "application/json" },
});

// Attach token on every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Auto-refresh on 401
api.interceptors.response.use(
  (res) => res,
  async (error) => {
    const original = error.config;
    if (error.response?.status === 401 && !original._retry) {
      original._retry = true;
      const refresh = localStorage.getItem("refresh_token");
      if (refresh) {
        try {
          const { data } = await axios.post(`${BASE_URL}/auth/refresh`, {
            refresh_token: refresh,
          });
          localStorage.setItem("access_token", data.access_token);
          localStorage.setItem("refresh_token", data.refresh_token);
          original.headers.Authorization = `Bearer ${data.access_token}`;
          return api(original);
        } catch {
          localStorage.clear();
          window.location.href = "/";
        }
      }
    }
    return Promise.reject(error);
  }
);

// ── Auth ──────────────────────────────────────────

export const authApi = {
  getLoginUrl: () => api.get<{ url: string }>("/auth/login"),
  getMe: () => api.get("/auth/me"),
  logout: () => api.post("/auth/logout"),
};

// ── Repositories ──────────────────────────────────

export const reposApi = {
  list: (skip = 0, limit = 20) =>
    api.get("/repositories", { params: { skip, limit } }),
  listGitHub: () => api.get("/repositories/github"),
  connect: (full_name: string) =>
    api.post("/repositories", { full_name }),
  get: (id: string) => api.get(`/repositories/${id}`),
  sync: (id: string) => api.post(`/repositories/${id}/sync`),
  disconnect: (id: string) => api.delete(`/repositories/${id}`),
};

// ── Analytics ─────────────────────────────────────

export const analyticsApi = {
  overview: (repoId: string) =>
    api.get(`/analytics/${repoId}/overview`),
  commitTrends: (repoId: string, days = 90) =>
    api.get(`/analytics/${repoId}/commits/trends`, { params: { days } }),
  prTrends: (repoId: string, days = 90) =>
    api.get(`/analytics/${repoId}/prs/trends`, { params: { days } }),
  issueTrends: (repoId: string, days = 90) =>
    api.get(`/analytics/${repoId}/issues/trends`, { params: { days } }),
  heatmap: (repoId: string) =>
    api.get(`/analytics/${repoId}/heatmap`),
  contributors: (repoId: string) =>
    api.get(`/analytics/${repoId}/contributors`),
  productivity: (repoId: string, days = 30) =>
    api.get(`/analytics/${repoId}/productivity`, { params: { days } }),
  trends: (repoId: string) =>
    api.get(`/analytics/${repoId}/trends`),
  languages: (repoId: string) =>
    api.get(`/analytics/${repoId}/languages`),
  compare: (repoA: string, repoB: string) =>
    api.get("/analytics/compare", { params: { repo_a: repoA, repo_b: repoB } }),
};