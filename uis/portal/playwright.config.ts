import { defineConfig, devices } from "@playwright/test";
import { randomBytes } from "node:crypto";
import path from "node:path";

const root = path.resolve(__dirname, "../..");
const secret = randomBytes(32).toString("hex");
const data = "/tmp/nexova-014-e2e";

export default defineConfig({
  testDir: "./e2e",
  timeout: 60_000,
  expect: { timeout: 20_000 },
  fullyParallel: false,
  workers: 1,
  reporter: "line",
  use: {
    baseURL: "http://127.0.0.1:3000",
    channel: "chrome",
    trace: "off",
    video: "off",
    screenshot: "off",
  },
  projects: [{ name: "chrome", use: { ...devices["Desktop Chrome"], channel: "chrome" } }],
  webServer: [
    {
      command: `mkdir -p ${data}/auth ${data}/suppliers ${data}/incidents && ${root}/services/api/.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000`,
      cwd: root,
      env: {
        ...process.env,
        JWT_SECRET: secret,
        ACCESS_TOKEN_EXPIRE_MINUTES: "30",
        AUTH_BCRYPT_ROUNDS: "4",
        AUTH_DATA_DIR: `${data}/auth`,
        SUPPLIERS_DATA_DIR: `${data}/suppliers`,
        INCIDENTS_DATA_DIR: `${data}/incidents`,
        SUPPLIERS_AUTOSEED: "1",
        EMAIL_TRANSPORT: "mock",
        PUBLIC_APP_URL: "http://127.0.0.1:3000",
        PASSWORD_RESET_EXPIRE_MINUTES: "30",
        PASSWORD_RESET_MAX_PER_HOUR: "5",
        PASSWORD_RESET_CAPTURE_FILE: `${data}/reset-link.txt`,
        PYTHONPATH: "packages:services/api",
      },
      url: "http://127.0.0.1:8000/docs",
      reuseExistingServer: false,
      timeout: 120_000,
    },
    {
      command: "npm run start",
      cwd: __dirname,
      url: "http://127.0.0.1:3000/login",
      reuseExistingServer: false,
      timeout: 120_000,
    },
    {
      command: "python3 -m http.server 4173 --bind 127.0.0.1",
      cwd: root,
      url: "http://127.0.0.1:4173/index.html",
      reuseExistingServer: false,
      timeout: 30_000,
    },
  ],
});
