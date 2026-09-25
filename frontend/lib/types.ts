export type View = 'chat' | 'calendar';

export type AuthState = {
  authenticated: boolean;
  email: string | null;
};

export type ChatResponse = {
  thread_id: string;
  status: 'success' | 'needs_approval' | 'cancelled' | 'error';
  message: string;
  events_affected: string[];
  pending_action: string | null;
};

export type ChatMessage = {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  response?: ChatResponse;
};

export type ApiError = {
  detail?: string;
};
