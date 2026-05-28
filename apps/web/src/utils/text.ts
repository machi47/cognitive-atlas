export function clampText(value: string, max = 420): string {
  if (value.length <= max) return value;
  return `${value.slice(0, max).trim()}...`;
}

