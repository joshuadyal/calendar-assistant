import { useEffect, useRef, useState } from 'react';
import type { FormEvent } from 'react';
import { logoutUser, sendChatMessage, submitApproval } from '../lib/api';
import type { AuthState, ChatMessage, ChatResponse, View } from '../lib/types';
import { CalendarView } from './CalendarView';
import { ChatView } from './ChatView';
import { Sidebar } from './Sidebar';
import { Topbar } from './Topbar';

type WorkspaceProps = {
  auth: AuthState;
  onSignedOut: () => void;
};

export function Workspace({ auth, onSignedOut }: WorkspaceProps) {
  const [view, setView] = useState<View>('chat');
  const [accountOpen, setAccountOpen] = useState(false);
  const [mobileNavOpen, setMobileNavOpen] = useState(false);
  const [month, setMonth] = useState(() => new Date());
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [draft, setDraft] = useState('');
  const [threadId, setThreadId] = useState<string | null>(null);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const endOfMessages = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endOfMessages.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, sending]);

  async function submitMessage(event: FormEvent) {
    event.preventDefault();
    const content = draft.trim();
    if (!content || sending) return;
    setError(null);
    setDraft('');
    setMessages((current) => [
      ...current,
      { id: crypto.randomUUID(), role: 'user', content },
    ]);
    setSending(true);
    try {
      const response = await sendChatMessage(content, threadId);
      setThreadId(response.thread_id);
      setMessages((current) => [
        ...current,
        {
          id: crypto.randomUUID(),
          role: 'assistant',
          content: response.message,
          response,
        },
      ]);
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : 'Unable to reach the assistant.',
      );
    } finally {
      setSending(false);
    }
  }

  async function decide(
    decision: 'approve' | 'reject',
    response: ChatResponse,
  ) {
    setError(null);
    setSending(true);
    try {
      const next = await submitApproval(response.thread_id, decision);
      setMessages((current) => [
        ...current,
        {
          id: crypto.randomUUID(),
          role: 'assistant',
          content: next.message,
          response: next,
        },
      ]);
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : 'Unable to process that decision.',
      );
    } finally {
      setSending(false);
    }
  }

  async function logout() {
    try {
      await logoutUser();
    } finally {
      setAccountOpen(false);
      setMessages([]);
      setThreadId(null);
      onSignedOut();
    }
  }

  function askAssistant() {
    setView('chat');
  }

  function askToday() {
    setView('chat');
    setDraft('What is on my calendar today?');
  }

  return (
    <div className="app-shell">
      <Topbar
        email={auth.email}
        accountOpen={accountOpen}
        onAccountToggle={() => setAccountOpen((open) => !open)}
        onLogout={logout}
        onMobileMenuToggle={() => setMobileNavOpen((open) => !open)}
      />
      <div className="workspace">
        <Sidebar
          view={view}
          conversationCount={
            messages.filter((message) => message.role === 'user').length
          }
          mobileOpen={mobileNavOpen}
          onViewChange={setView}
          onClose={() => setMobileNavOpen(false)}
        />
        <main className="main-content">
          {view === 'chat' ? (
            <ChatView
              messages={messages}
              draft={draft}
              sending={sending}
              error={error}
              endOfMessages={endOfMessages}
              onDraftChange={setDraft}
              onSubmit={submitMessage}
              onDecision={decide}
            />
          ) : (
            <CalendarView
              month={month}
              onMonthChange={setMonth}
              onAskAssistant={askAssistant}
              onAskToday={askToday}
            />
          )}
        </main>
      </div>
    </div>
  );
}
