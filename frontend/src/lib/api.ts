const API_BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8000/api";

export async function api<T>(path: string, options: RequestInit = {}): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  if (!res.ok) {
    let detail = "";
    try {
      const data = await res.json();
      detail = (data as any).detail || JSON.stringify(data);
    } catch {
      detail = res.statusText;
    }
    throw new Error(`Erro ${res.status}: ${detail}`);
  }

  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}
