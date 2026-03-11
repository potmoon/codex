export function cn(...classes: Array<string | undefined | false>): string {
  return classes.filter(Boolean).join(" ");
}

export function prettyJson(value: unknown): string {
  return JSON.stringify(value, null, 2);
}
