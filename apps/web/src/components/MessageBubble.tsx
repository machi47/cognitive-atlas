import ReactMarkdown, { type Components } from "react-markdown";
import remarkGfm from "remark-gfm";
import type { Turn } from "../api/types";
import { clampText } from "../utils/text";
import { formatShortTime } from "../utils/time";

const markdownComponents: Components = {
  a: ({ children, ...props }) => (
    <a {...props} target="_blank" rel="noreferrer">
      {children}
    </a>
  ),
};

export default function MessageBubble({ turn }: { turn: Turn; onInspector?: () => void }) {
  const isUser = turn.role === "user";
  const content = isUser && turn.content.length > 700 ? clampText(turn.content, 700) : turn.content;
  return (
    <article className={`message ${turn.role}`}>
      <header>
        <span>{isUser ? "You" : "Research Partner"}</span>
        <time>{formatShortTime(turn.created_at)}</time>
      </header>
      {isUser ? (
        <div className="message-body plain-message">{content}</div>
      ) : (
        <div className="message-body markdown-body">
          <ReactMarkdown remarkPlugins={[remarkGfm]} components={markdownComponents}>
            {content}
          </ReactMarkdown>
        </div>
      )}
    </article>
  );
}
