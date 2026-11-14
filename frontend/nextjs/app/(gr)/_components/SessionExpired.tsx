'use client';

import { LOGIN_PATH, redirectToLogin } from '@/lib/research/authErrors';

/** Clear session-expired / forbidden message with a sign-in action. :-) */
export default function SessionExpired({
  message = 'Your session has expired. Sign in again to continue.',
  className = '',
}: {
  message?: string;
  className?: string;
}) {
  return (
    <p role="alert" className={`text-[14px] text-rubric ${className}`.trim()}>
      {message}{' '}
      <button type="button" className="underline" onClick={() => redirectToLogin()}>
        Sign in
      </button>
      <span className="sr-only"> ({LOGIN_PATH})</span>
    </p>
  );
}
