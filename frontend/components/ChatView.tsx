import { FormEvent, RefObject } from 'react';
import { Clock3, Send, Sparkles, UserRound } from 'lucide-react';
import type { ChatMessage, ChatResponse } from '../lib/types';

type ChatViewProps = {
  messages: ChatMessage[];
  draft: string;
  sending: boolean;
  error: string | null;
  endOfMessages: RefObject<HTMLDivElement | null>;
  onDraftChange: (value: string) => void;
  onSubmit: (event: FormEvent) => void;
  onDecision: (decision: 'approve' | 'reject', response: ChatResponse) => void;
};

export function ChatView({
  messages,
  draft,
  sending,
  error,
  endOfMessages,
  onDraftChange,
  onSubmit,
  onDecision,
}: ChatViewProps) {
  return (
    <section className="agent-view">
      <div className="content-header">
        <div>
          <p className="eyebrow">ASSISTANT</p>
          <h2>What would you like to plan?</h2>
          <p className="section-subtitle">
            Ask about your schedule or make a change to your calendar.
          </p>
        </div>
        <div className="agent-badge">
          <span className="pulse-dot" /> Ready
        </div>
      </div>
      <div className="chat-layout">
        <div className="chat-panel">
          <div className="messages" aria-live="polite">
            {messages.length === 0 && (
              <EmptyChat onSuggestion={onDraftChange} />
            )}
            {messages.map((message) => (
              <Message
                key={message.id}
                message={message}
                sending={sending}
                onDecision={onDecision}
              />
            ))}
            {sending && (
              <div className="message-row assistant">
                <div className="message-avatar">
                  <Sparkles size={15} />
                </div>
                <div className="message-bubble typing">
                  <span />
                  <span />
                  <span />
                </div>
              </div>
            )}
            <div ref={endOfMessages} />
          </div>
          {error && <div className="error-banner">{error}</div>}
          <form className="composer" onSubmit={onSubmit}>
            <input
              value={draft}
              onChange={(event) => onDraftChange(event.target.value)}
              placeholder="Ask your calendar assistant..."
              aria-label="Message the calendar assistant"
              disabled={sending}
            />
            <button
              className="send-button"
              aria-label="Send message"
              disabled={!draft.trim() || sending}
            >
              <Send size={17} />
            </button>
          </form>
          <p className="composer-note">
            The assistant will ask before making calendar changes.
          </p>
        </div>
        <ActivityPanel messages={messages} />
      </div>
    </section>
  );
}

function EmptyChat({
  onSuggestion,
}: {
  onSuggestion: (value: string) => void;
}) {
  return (
    <div className="empty-chat">
      <div className="empty-icon">
        <Sparkles size={21} />
      </div>
      <h3>A calmer way to plan</h3>
      <p>
        Try a question like “What is on my calendar tomorrow?” or “Find me a
        free hour this afternoon.”
      </p>
      <div className="suggestions">
        <button
          onClick={() => onSuggestion('What is on my calendar tomorrow?')}
        >
          Tomorrow’s schedule
        </button>
        <button
          onClick={() => onSuggestion('Find me a free hour this afternoon')}
        >
          Find free time
        </button>
      </div>
    </div>
  );
}

function Message({
  message,
  sending,
  onDecision,
}: {
  message: ChatMessage;
  sending: boolean;
  onDecision: ChatViewProps['onDecision'];
}) {
  return (
    <div className={`message-row ${message.role}`}>
      <div className="message-avatar">
        {message.role === 'assistant' ? (
          <Sparkles size={15} />
        ) : (
          <UserRound size={15} />
        )}
      </div>
      <div className="message-bubble">
        <p>{message.content}</p>
        {message.response?.pending_action &&
          message.response.status === 'needs_approval' && (
            <div className="approval-box">
              <div>
                <strong>Approval needed</strong>
                <span>
                  {message.response.pending_action.replaceAll('_', ' ')}
                </span>
              </div>
              <div className="approval-actions">
                <button
                  className="secondary-button"
                  disabled={sending}
                  onClick={() => onDecision('reject', message.response!)}
                >
                  Reject
                </button>
                <button
                  className="primary-button"
                  disabled={sending}
                  onClick={() => onDecision('approve', message.response!)}
                >
                  Approve
                </button>
              </div>
            </div>
          )}
        {message.response?.events_affected?.length ? (
          <div className="affected-events">
            <Clock3 size={14} /> {message.response.events_affected.length} event
            {message.response.events_affected.length === 1 ? '' : 's'} affected
          </div>
        ) : null}
      </div>
    </div>
  );
}

function ActivityPanel({ messages }: { messages: ChatMessage[] }) {
  const userMessages = messages.filter((message) => message.role === 'user');
  return (
    <aside className="activity-panel">
      <div className="panel-title">
        <span>RECENT ACTIVITY</span>
        <Clock3 size={15} />
      </div>
      {messages.length === 0 ? (
        <div className="activity-empty">
          Your conversations and calendar actions will appear here.
        </div>
      ) : (
        <div className="activity-list">
          {userMessages
            .slice(-5)
            .reverse()
            .map((message) => (
              <div className="activity-item" key={message.id}>
                <span className="activity-line" />
                <div>
                  <span className="activity-time">JUST NOW</span>
                  <p>{message.content}</p>
                </div>
              </div>
            ))}
        </div>
      )}
    </aside>
  );
}
