import AuthCallbackClient from './AuthCallbackClient';

type CallbackSearchParams = Promise<{
  google_auth?: string;
  error?: string;
}>;

export default async function AuthCallbackPage({
  searchParams,
}: {
  searchParams: CallbackSearchParams;
}) {
  const params = await searchParams;

  return (
    <AuthCallbackClient
      googleAuth={params.google_auth}
      errorMessage={params.error}
    />
  );
}
