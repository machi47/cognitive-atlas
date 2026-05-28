import { ApiError } from "../api/client";

type ErrorBody = {
  error?: {
    code?: string;
    message?: string;
    details?: {
      provider?: string;
      reason?: string;
      stderr_summary?: string;
      next_commands?: string[];
    };
  };
};

export default function ModelErrorCard({ error, onDismiss }: { error: Error; onDismiss?: () => void }) {
  const body = error instanceof ApiError ? (error.details as ErrorBody) : {};
  const details = body.error?.details || {};
  const text = [
    body.error?.message || error.message,
    details.provider ? `Provider: ${details.provider}` : "",
    details.reason ? `Reason: ${details.reason}` : "",
    details.stderr_summary ? `stderr: ${details.stderr_summary}` : "",
    details.next_commands?.length ? `Next: ${details.next_commands.join("  |  ")}` : ""
  ].filter(Boolean).join("\n");

  return (
    <div className="error-state model-error">
      <strong>Model unavailable</strong>
      <span>{body.error?.message || error.message}</span>
      {details.provider && <small>Provider: {details.provider}</small>}
      {details.reason && <small>Reason: {details.reason}</small>}
      {details.stderr_summary && <pre>{details.stderr_summary}</pre>}
      {details.next_commands?.length ? (
        <code>{details.next_commands.join("  |  ")}</code>
      ) : null}
      <div className="error-actions">
        <button onClick={() => navigator.clipboard?.writeText(text)}>Copy error</button>
        {onDismiss && <button onClick={onDismiss}>Dismiss</button>}
      </div>
    </div>
  );
}
