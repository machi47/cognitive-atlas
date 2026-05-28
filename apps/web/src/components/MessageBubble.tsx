import type { Turn } from "../api/types";
import { clampText } from "../utils/text";
import { formatShortTime } from "../utils/time";

export default function MessageBubble({ turn }: { turn: Turn; onInspector?: () => void }) {
  const isUser = turn.role === "user";
  const content = isUser && turn.content.length > 700 ? clampText(turn.content, 700) : turn.content;
  return (
    <article className={`message ${turn.role}`}>
      <header>
        <span>{isUser ? "You" : "Assistant"}</span>
        <time>{formatShortTime(turn.created_at)}</time>
      </header>
      <p>{content}</p>
    </article>
  );
}
