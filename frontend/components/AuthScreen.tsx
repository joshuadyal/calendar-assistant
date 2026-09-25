import { CalendarDays } from 'lucide-react';
import { googleLoginUrl } from '../lib/api';

export function AuthScreen({ error }: { error?: string | null }) {
  return (
    <main className="auth-screen">
      <div className="auth-panel">
        <div className="brand-mark">
          <CalendarDays size={23} />
        </div>
        <p className="eyebrow">PERSONAL CALENDAR ASSISTANT</p>
        <h1>Your time, in focus.</h1>
        <p className="auth-copy">
          Connect Google Calendar to ask questions, find open time, and manage
          events with a clear approval step.
        </p>
        {error && <div className="error-banner auth-error">{error}</div>}
        <a className="primary-button auth-button" href={googleLoginUrl()}>
          <CalendarDays size={17} /> Continue with Google
        </a>
        <p className="privacy-note">
          Your calendar stays connected to your Google account.
        </p>
      </div>
      <div className="auth-aside">
        <span>01</span>
        <p>Ask for the shape of your day.</p>
        <span>02</span>
        <p>Review every change.</p>
      </div>
    </main>
  );
}
