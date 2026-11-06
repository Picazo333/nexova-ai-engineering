export const LOCKUP_BREAKPOINT_PX = 640;

export type LockupVariant = "stacked" | "wide";

export type LockupBox = {
  variant: LockupVariant;
  width: number;
  height: number;
};

const stacked: LockupBox = { variant: "stacked", width: 280, height: 140 };
const wide: LockupBox = { variant: "wide", width: 400, height: 64 };

export function lockupFrame(viewportWidth: number): LockupBox {
  if (viewportWidth >= LOCKUP_BREAKPOINT_PX) return wide;
  return stacked;
}
