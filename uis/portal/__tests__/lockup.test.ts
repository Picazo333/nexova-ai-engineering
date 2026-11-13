import { LOCKUP_BREAKPOINT_PX, lockupFrame } from "@/lib/lockup";

describe("caja reservada del lockup", () => {
  test("por debajo de 640 px reserva el apilado a 280×140", () => {
    expect(LOCKUP_BREAKPOINT_PX).toBe(640);
    expect(lockupFrame(0)).toEqual({ variant: "stacked", width: 280, height: 140 });
    expect(lockupFrame(639)).toEqual({ variant: "stacked", width: 280, height: 140 });
  });

  test("desde 640 px reserva el horizontal a 400×64", () => {
    expect(lockupFrame(640)).toEqual({ variant: "wide", width: 400, height: 64 });
    expect(lockupFrame(1280)).toEqual({ variant: "wide", width: 400, height: 64 });
  });

  test("la proporción coincide con el SVG para no deformarlo", () => {
    const stacked = lockupFrame(390);
    const wide = lockupFrame(1280);
    expect(stacked.width / stacked.height).toBeCloseTo(600 / 300);
    expect(wide.width / wide.height).toBeCloseTo(1000 / 160);
  });
});
