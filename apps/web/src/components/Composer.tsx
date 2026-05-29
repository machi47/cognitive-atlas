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
  const [hint, setHint] = useState("");
  const [listening, setListening] = useState(false);
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
    const content = value.trim();
    if (!content || disabled) return;
    setValue("");
    onSend(content);
  };

  const onKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>) => {
    if ((event.metaKey || event.ctrlKey) && event.key === "Enter") {
      submit();
    }
  };

  const startVoice = () => {
    type SpeechCtor = new () => {
      continuous: boolean;
      interimResults: boolean;
      lang: string;
      onresult: ((event: { results: ArrayLike<{ 0: { transcript: string } }> }) => void) | null;
      onerror: (() => void) | null;
      onend: (() => void) | null;
      start: () => void;
    };
    const win = window as typeof window & { SpeechRecognition?: SpeechCtor; webkitSpeechRecognition?: SpeechCtor };
    const Recognition = win.SpeechRecognition || win.webkitSpeechRecognition;
    if (!Recognition) {
      ref.current?.focus();
      setHint("Voice capture is handled by your keyboard dictation here.");
      return;
    }
    const recognition = new Recognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = "en-US";
    recognition.onresult = (event) => {
      const transcript = Array.from(event.results).map((result) => result[0].transcript).join(" ");
      setValue((current) => `${current}${current ? " " : ""}${transcript}`.trim());
    };
    recognition.onerror = () => {
      setHint("Voice capture failed. Try keyboard dictation.");
      setListening(false);
    };
    recognition.onend = () => setListening(false);
    setListening(true);
    recognition.start();
  };

  const parsed = parseCommand(value);

  return (
    <form className="composer" onSubmit={submit}>
      <div className="composer-box">
        <textarea
          ref={ref}
          value={value}
          onChange={(event) => setValue(event.target.value)}
          onKeyDown={onKeyDown}
          placeholder="Continue the technical thread."
          disabled={disabled}
        />
        <div className="composer-actions">
          <button type="button" className="icon-button" title="More input options" aria-label="More input options" onClick={onPlus}>
            <Plus size={18} />
          </button>
          {parsed.command && <span className="command-chip">/{parsed.command}</span>}
          <button type="button" className="icon-button" title="Voice input" aria-label="Voice input" onClick={startVoice} data-active={listening ? "true" : "false"}>
            <Mic size={18} />
          </button>
          <button type="submit" className="send-button" disabled={disabled || !value.trim()}>
            <Send size={18} /> Send
          </button>
        </div>
      </div>
      {hint && <small className="composer-hint">{hint}</small>}
    </form>
  );
}
