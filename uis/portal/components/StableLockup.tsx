import { LOCKUP_BREAKPOINT_PX, lockupFrame } from "@/lib/lockup";

export function StableLockup() {
  const stacked = lockupFrame(0);
  const wide = lockupFrame(LOCKUP_BREAKPOINT_PX);
  return (
    <div className="footer-lockup">
      <img
        className="lockup-stacked"
        src="/brand/lockups/signal-stacked.svg"
        alt="4Geeks por Divinivid"
        width={stacked.width}
        height={stacked.height}
      />
      <img
        className="lockup-wide"
        src="/brand/lockups/signal-horizontal.svg"
        alt="4Geeks por Divinivid"
        width={wide.width}
        height={wide.height}
      />
    </div>
  );
}
