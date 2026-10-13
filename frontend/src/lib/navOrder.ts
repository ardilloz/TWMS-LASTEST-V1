// Global sidebar menu ordering, set by the main admin and applied for every user.
export type NavOrder = { groups: string[]; items: Record<string, string[]>; singles: string[] };

// Stable reorder: known keys follow `order`; unknown keys keep their original relative position (placed last).
export function applyOrder<T>(arr: T[], keyOf: (t: T) => string, order?: string[]): T[] {
  if (!order || order.length === 0) return arr;
  const rank = new Map(order.map((k, i) => [k, i] as const));
  return arr
    .map((item, i) => ({ item, i }))
    .sort((a, b) => {
      const ra = rank.has(keyOf(a.item)) ? (rank.get(keyOf(a.item)) as number) : Infinity;
      const rb = rank.has(keyOf(b.item)) ? (rank.get(keyOf(b.item)) as number) : Infinity;
      return ra !== rb ? ra - rb : a.i - b.i;
    })
    .map((x) => x.item);
}

// Move `fromKey` to the position of `toKey` within a key list.
export function moveKey(keys: string[], fromKey: string, toKey: string): string[] {
  if (fromKey === toKey) return keys;
  const next = keys.filter((k) => k !== fromKey);
  const at = next.indexOf(toKey);
  if (at === -1) return keys;
  next.splice(at, 0, fromKey);
  return next;
}
