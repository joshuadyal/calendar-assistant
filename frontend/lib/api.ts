import type { ApiError, AuthState, ChatResponse } from './types';

export const API_URL =
  process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';

async function requestJson<T>(
  input: RequestInfo | URL,
  init?: RequestInit,
): Promise<T> {
  const response = await fetch(input, {
    ...init,
    credentials: 'include',
  });
  const data = (await response.json()) as T | ApiError;

  if (!response.ok) {
    const errorData = data as ApiError;
    const detail = errorData.detail ?? 'The request could not be completed.';
    throw new Error(detail);
  }

  return data as T;
}

export function googleLoginUrl() {
  return `${API_URL}/auth/google/login`;
}

export function getCurrentUser() {
  return requestJson<AuthState>(`${API_URL}/auth/me`);
}

export function logoutUser() {
  return requestJson<AuthState>(`${API_URL}/auth/logout`, { method: 'POST' });
}

export function sendChatMessage(message: string, threadId: string | null) {
  return requestJson<ChatResponse>(`${API_URL}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, thread_id: threadId }),
  });
}

export function submitApproval(
  threadId: string,
  decision: 'approve' | 'reject',
) {
  return requestJson<ChatResponse>(`${API_URL}/chat/${threadId}/approval`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ decision }),
  });
}
