export function LoadingStatus({ label }: { label: string }) {
  return (
    <p className="feedback feedback-status" role="status">
      {label}
    </p>
  );
}

export function ErrorStatus({
  message,
  onRetry,
}: {
  message: string;
  onRetry?: () => void;
}) {
  return (
    <div className="feedback feedback-error" role="alert">
      <p>{message}</p>
      {onRetry ? (
        <button className="button button-secondary" type="button" onClick={onRetry}>
          Reintentar
        </button>
      ) : null}
    </div>
  );
}

export function EmptyStatus({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="empty">
      <h2>{title}</h2>
      {children}
    </div>
  );
}
