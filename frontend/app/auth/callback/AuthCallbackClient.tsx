'use client';

import { useEffect, useState } from 'react';
import { CalendarDays } from 'lucide-react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { getCurrentUser, googleLoginUrl } from '../../../lib/api';
import { LoadingScreen } from '../../../components/LoadingScreen';

type CallbackState = 'checking' | 'success' | 'error';

type AuthCallbackClientProps = {
  googleAuth?: string;
  errorMessage?: string;
};

export default function AuthCallbackClient({
  googleAuth,
  errorMessage,
}: AuthCallbackClientProps) {
  const router = useRouter();
  const [state, setState] = useState<CallbackState>(
    googleAuth === 'error' ? 'error' : 'checking',
  );
  const error =
    errorMessage ?? 'Google sign-in was not completed. Please try again.';

  useEffect(() => {
    if (googleAuth === 'error') return;

    getCurrentUser()
      .then((user) => {
        if (user.authenticated) {
          setState('success');
          router.replace('/');
        } else {
          setState('error');
        }
      })
      .catch(() => setState('error'));
  }, [googleAuth, router]);

  if (state === 'checking' || state === 'success') {
    return (
      <LoadingScreen
        label={
          state === 'success'
            ? 'Opening your workspace'
            : 'Confirming your Google sign-in'
        }
      />
    );
  }

  return (
    <main className="auth-screen">
      <div className="auth-panel">
        <div className="brand-mark">
          <CalendarDays size={23} />
        </div>
        <p className="eyebrow">GOOGLE SIGN-IN</p>
        <h1>We couldn’t connect.</h1>
        <div className="error-banner auth-error">{error}</div>
        <p className="auth-copy">
          The Google session may have expired or your browser may have blocked
          the temporary login cookie. Start a fresh sign-in to try again.
        </p>
        <a className="primary-button auth-button" href={googleLoginUrl()}>
          <CalendarDays size={17} /> Try Google sign-in again
        </a>
        <Link className="callback-home-link" href="/">
          Return to home
        </Link>
      </div>
    </main>
  );
}
