import { FormEvent, KeyboardEvent, useEffect, useRef, useState } from "react";
import { Mic, Plus, Send } from "lucide-react";
import { parseCommand } from "../utils/commands";

type ComposerProps = {
  onSend: (content: string) => void;
  disabled?: boolean;
  clearKey?: number;
  onPlus?: () => void;
};

export default function Composer({ onSend, disabled, clearKey = 0, onPlus }: ComposerProps) {
  const [value, setValue] = useState("");
  const ref = useRef<HTMLTextAreaElement | null>(null);

  useEffect(() => {
    if (!ref.current) return;
    ref.current.style.height = "auto";
    ref.current.style.height = `${Math.min(ref.current.scrollHeight, 220)}px`;
  }, [value]);

  useEffect(() => {
    setValue("");
  }, [clearKey]);

  const submit = (event?: FormEvent) => {
    event?.preventDefault();
    if (!value.trim() || disabled) return;
    onSend(value);
  };

  const onKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>) => {
    if ((event.metaKey || event.ctrlKey) && event.key === "Enter") {
      submit();
    }
  };

  const parsed = parseCommand(value);

  return (
    <form className="composer" onSubmit={submit}>
      <textarea
        ref={ref}
        value={value}
        onChange={(event) => setValue(event.target.value)}
        onKeyDown={onKeyDown}
        placeholder="Dump the thought. It can be messy."
        disabled={disabled}
      />
      <div className="composer-actions">
        <button type="button" className="icon-button" title="More input options" aria-label="More input options" onClick={onPlus}>
          <Plus size={18} />
        </button>
        {parsed.command && <span className="command-chip">/{parsed.command}</span>}
        <button type="button" className="icon-button" title="Voice placeholder" aria-label="Voice placeholder">
          <Mic size={18} />
        </button>
        <button type="submit" className="send-button" disabled={disabled || !value.trim()}>
          <Send size={18} /> Send
        </button>
      </div>
    </form>
  );
}
