"use client";

type ErrorBannerProps = {
  title: string;
  message: string;
  onRetry?: () => void;
  retryLabel?: string;
  heading?: "h1" | "h2";
  alertRef?: React.Ref<HTMLDivElement>;
};

export function ErrorBanner({
  title,
  message,
  onRetry,
  retryLabel = "Reintentar",
  heading = "h2",
  alertRef,
}: ErrorBannerProps) {
  const Heading = heading;
  return (
    <div className="banner" role="alert" tabIndex={-1} ref={alertRef}>
      <Heading>{title}</Heading>
      <p>{message}</p>
      {onRetry ? (
        <p className="actions">
          <button type="button" onClick={onRetry}>
            {retryLabel}
          </button>
        </p>
      ) : null}
    </div>
  );
}

export function LoadingState({ label }: { label: string }) {
  return (
    <p className="loading-state" role="status" aria-live="polite">
      <span className="loading-mark" aria-hidden="true" />
      {label}
    </p>
  );
}

export function EmptyState({
  title,
  message,
  href,
  action,
}: {
  title: string;
  message: string;
  href: string;
  action: string;
}) {
  return (
    <div className="empty">
      <h2>{title}</h2>
      <p>{message}</p>
      <p className="actions">
        <a className="button" href={href}>
          {action}
        </a>
      </p>
    </div>
  );
}
