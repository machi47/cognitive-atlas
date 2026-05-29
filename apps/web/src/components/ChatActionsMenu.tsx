import { BookOpen, Download, GitFork, Network, Plus, Search, Trash2, X } from "lucide-react";
import type { Session } from "../api/types";

type Props = {
  session?: Session | null;
  onClose: () => void;
  onNewChat: () => void;
  onDelete?: () => void;
  onFork?: () => void;
  onInspector?: () => void;
};

export default function ChatActionsMenu({ session, onClose, onNewChat, onDelete, onFork, onInspector }: Props) {
  const exportUrl = session ? `/api/export/session/${session.id}.md` : undefined;
  return (
    <div className="action-sheet-backdrop" onClick={onClose}>
      <div className="action-sheet" onClick={(event) => event.stopPropagation()}>
        <div className="action-sheet-header">
          <strong>Chat actions</strong>
          <button className="icon-button" onClick={onClose} aria-label="Close actions"><X size={18} /></button>
        </div>
        <button onClick={onNewChat}><Plus size={18} /> New chat</button>
        <a href="/sessions"><Search size={18} /> All chats</a>
        <a href="/atlas"><Network size={18} /> Learn Workbench</a>
        <a href="/sources"><BookOpen size={18} /> Sources</a>
        {exportUrl && <a href={exportUrl} target="_blank" rel="noreferrer"><Download size={18} /> Export this chat</a>}
        {onInspector && <button onClick={onInspector}><Network size={18} /> Inspector</button>}
        {onFork && <button onClick={onFork}><GitFork size={18} /> Fork chat</button>}
        {onDelete && <button className="danger-action" onClick={onDelete}><Trash2 size={18} /> Delete chat</button>}
      </div>
    </div>
  );
}
