import type {
  ApiErrorBody,
  Obligation,
  ObligationCreateInput,
  ObligationDetail,
  ObligationUpdateInput,
  Status,
  TransitionInput,
} from "./types";

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    public readonly code: string,
    message: string,
    public readonly details?: Record<string, unknown>,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...init?.headers,
    },
  });

  if (!response.ok) {
    const body = (await response.json().catch(() => ({
      code: "UNKNOWN",
      message: response.statusText,
    }))) as ApiErrorBody;
    throw new ApiError(response.status, body.code, body.message, body.details);
  }

  return (await response.json()) as T;
}

function buildQuery(params: Record<string, string | number | boolean | undefined>): string {
  const search = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined) {
      search.set(key, String(value));
    }
  }
  const qs = search.toString();
  return qs ? `?${qs}` : "";
}

export const api = {
  listObligations(params?: { status?: Status; overdue?: boolean }): Promise<Obligation[]> {
    return request<Obligation[]>(`/api/obligations${buildQuery(params ?? {})}`);
  },

  getObligation(id: string): Promise<ObligationDetail> {
    return request<ObligationDetail>(`/api/obligations/${id}`);
  },

  createObligation(input: ObligationCreateInput): Promise<ObligationDetail> {
    return request<ObligationDetail>("/api/obligations", {
      method: "POST",
      body: JSON.stringify(input),
    });
  },

  updateObligation(
    id: string,
    input: ObligationUpdateInput,
  ): Promise<ObligationDetail> {
    return request<ObligationDetail>(`/api/obligations/${id}`, {
      method: "PATCH",
      body: JSON.stringify(input),
    });
  },

  transition(id: string, input: TransitionInput): Promise<ObligationDetail> {
    return request<ObligationDetail>(`/api/obligations/${id}/transitions`, {
      method: "POST",
      body: JSON.stringify(input),
    });
  },

  uploadDocument(id: string, file: File): Promise<{ id: string; filename: string; size: number }> {
    const formData = new FormData();
    formData.append("file", file);
    return request<{ id: string; filename: string; size: number }>(
      `/api/obligations/${id}/documents`,
      {
        method: "POST",
        body: formData,
        headers: {},
      },
    );
  },
};
