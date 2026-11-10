import type { Config } from "jest";

const config: Config = {
  testEnvironment: "node",
  roots: ["<rootDir>/__tests__"],
  testMatch: ["**/*.test.ts"],
  moduleNameMapper: {
    "^@/(.*)$": "<rootDir>/$1",
  },
  collectCoverageFrom: ["lib/session.ts", "lib/forms.ts", "lib/paths.ts", "lib/http-messages.ts"],
  coveragePathIgnorePatterns: ["/node_modules/"],
  transform: {
    "^.+\\.tsx?$": [
      "ts-jest",
      {
        tsconfig: {
          esModuleInterop: true,
          module: "commonjs",
          moduleResolution: "node",
          strict: true,
          target: "ES2022",
          types: ["jest", "node"],
        },
      },
    ],
  },
};

export default config;
