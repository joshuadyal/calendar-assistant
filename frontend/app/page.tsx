'use client';

import { useEffect, useState } from 'react';
import { AuthScreen } from '../components/AuthScreen';
import { LoadingScreen } from '../components/LoadingScreen';
import { Workspace } from '../components/Workspace';
import { getCurrentUser } from '../lib/api';
import type { AuthState } from '../lib/types';

export default function Home() {
  const [auth, setAuth] = useState<AuthState | null>(null);
  const [error] = useState<string | null>(() =>
    typeof window !== 'undefined' &&
    new URLSearchParams(window.location.search).get('google_auth') === 'error'
      ? (new URLSearchParams(window.location.search).get('error') ??
        'Google sign-in was not completed. Please try again.')
      : null,
  );

  useEffect(() => {
    getCurrentUser()
      .then(setAuth)
      .catch(() => setAuth({ authenticated: false, email: null }));
  }, []);

  if (auth === null) return <LoadingScreen />;
  if (!auth.authenticated) return <AuthScreen error={error} />;
  return (
    <Workspace
      auth={auth}
      onSignedOut={() => setAuth({ authenticated: false, email: null })}
    />
  );
}
