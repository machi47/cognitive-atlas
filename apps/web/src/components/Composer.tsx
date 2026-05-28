import { FormEvent, KeyboardEvent, useEffect, useRef, useState } from "react";
import { Mic, Send } from "lucide-react";
import { parseCommand } from "../utils/commands";

type ComposerProps = {
  onSend: (content: string) => void;
  disabled?: boolean;
  mode: string;
  onModeChange: (mode: string) => void;
};

export default function Composer({ onSend, disabled, mode, onModeChange }: ComposerProps) {
  const [value, setValue] = useState("");
  const ref = useRef<HTMLTextAreaElement | null>(null);

  useEffect(() => {
    if (!ref.current) return;
    ref.current.style.height = "auto";
    ref.current.style.height = `${Math.min(ref.current.scrollHeight, 220)}px`;
  }, [value]);

  const submit = (event?: FormEvent) => {
    event?.preventDefault();
    if (!value.trim() || disabled) return;
    onSend(value);
    setValue("");
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
        <select value={mode} onChange={(event) => onModeChange(event.target.value)} aria-label="Response mode">
          <option value="discuss">Discuss</option>
          <option value="explain">Explain</option>
          <option value="research">Research</option>
          <option value="critique">Critique</option>
          <option value="map">Map</option>
          <option value="compress">Compress</option>
          <option value="quiz">Quiz</option>
          <option value="deep">Deep</option>
        </select>
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

