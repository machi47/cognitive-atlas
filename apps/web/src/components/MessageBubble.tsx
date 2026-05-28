import { BookOpen, GitFork, Map, MoreHorizontal, ThumbsUp, TriangleAlert } from "lucide-react";
import type { Turn } from "../api/types";
import { clampText } from "../utils/text";
import { formatShortTime } from "../utils/time";

export default function MessageBubble({ turn, onInspector }: { turn: Turn; onInspector: () => void }) {
  const isUser = turn.role === "user";
  const content = isUser && turn.content.length > 700 ? clampText(turn.content, 700) : turn.content;
  return (
    <article className={`message ${turn.role}`}>
      <header>
        <span>{isUser ? "You" : "Atlas"}</span>
        <time>{formatShortTime(turn.created_at)}</time>
      </header>
      <p>{content}</p>
      {!isUser && (
        <div className="message-actions">
          <button title="Good"><ThumbsUp size={15} /> Good</button>
          <button title="Too much"><TriangleAlert size={15} /> Too much</button>
          <button onClick={onInspector} title="Show map impact"><Map size={15} /> Impact</button>
          <button onClick={onInspector} title="Sources"><BookOpen size={15} /> Sources</button>
          <button title="Fork from here"><GitFork size={15} /> Fork</button>
          <button title="More"><MoreHorizontal size={15} /></button>
        </div>
      )}
    </article>
  );
}

