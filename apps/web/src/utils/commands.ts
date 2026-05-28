export type ParsedCommand = { command: string | null; content: string };

export function parseCommand(value: string): ParsedCommand {
  const match = value.trim().match(/^\/([a-zA-Z][\w-]*)(?:\s+(.*))?$/);
  if (!match) return { command: null, content: value };
  return { command: match[1].toLowerCase(), content: match[2] || "" };
}

export function modeForCommand(command: string | null, currentMode: string): string {
  if (!command) return currentMode;
  const map: Record<string, string> = {
    deepen: "deep",
    map: "map",
    sources: "source",
    criticize: "critique",
    compress: "compress",
    quiz: "quiz",
    research: "research",
    trace: "trace"
  };
  return map[command] || currentMode;
}

