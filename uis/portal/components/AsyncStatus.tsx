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
    <div className="alert error-banner" role="alert" tabIndex={-1} ref={alertRef}>
      <Heading>{title}</Heading>
      <p>{message}</p>
      <p className="actions">
        {onRetry ? (
          <button className="button" type="button" onClick={onRetry}>
            {retryLabel}
          </button>
        ) : null}
        <a className="button secondary" href="/">
          Ir al inicio
        </a>
      </p>
      <p className="note">Si se repite, contacta con el soporte interno de Nexova.</p>
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
