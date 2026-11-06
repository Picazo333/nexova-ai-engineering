export function createRequestGuard() {
  let current = 0;
  return {
    next(): number {
      current += 1;
      return current;
    },
    isCurrent(id: number): boolean {
      return id === current;
    },
  };
}
