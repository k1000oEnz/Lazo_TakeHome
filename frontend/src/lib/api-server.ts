const API_BASE = process.env.BACKEND_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    public readonly code: string,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...init?.headers },
  });
  if (!res.ok) {
    const body = (await res.json().catch(() => ({}))) as { code?: string; message?: string };
    throw new ApiError(res.status, body.code ?? "UNKNOWN", body.message ?? res.statusText);
  }
  return (await res.json()) as T;
}

export const serverApi = {
  getObligation(id: string) {
    return request(`/api/obligations/${id}`);
  },
  transition(
    id: string,
    body: { to_status: string; version: number; document_id?: string },
  ) {
    return request(`/api/obligations/${id}/transitions`, {
      method: "POST",
      body: JSON.stringify(body),
    });
  },
  async uploadDocument(id: string, file: File) {
    const fd = new FormData();
    fd.append("file", file);
    const res = await fetch(`${API_BASE}/api/obligations/${id}/documents`, {
      method: "POST",
      body: fd,
    });
    if (!res.ok) {
      const body = (await res.json().catch(() => ({}))) as { code?: string; message?: string };
      throw new ApiError(res.status, body.code ?? "UNKNOWN", body.message ?? res.statusText);
    }
    return res.json();
  },
  createObligation(body: Record<string, unknown>) {
    return request("/api/obligations", {
      method: "POST",
      body: JSON.stringify(body),
    });
  },
  updateObligation(id: string, body: Record<string, unknown>) {
    return request(`/api/obligations/${id}`, {
      method: "PATCH",
      body: JSON.stringify(body),
    });
  },
};
