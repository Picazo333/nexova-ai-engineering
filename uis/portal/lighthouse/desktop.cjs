module.exports = {
  extends: "lighthouse:default",
  settings: {
    formFactor: "desktop",
    throttlingMethod: "simulate",
    onlyCategories: ["performance"],
    throttling: {
      rttMs: 40,
      throughputKbps: 10240,
      cpuSlowdownMultiplier: 1,
      requestLatencyMs: 0,
      downloadThroughputKbps: 10240,
      uploadThroughputKbps: 10240,
    },
    screenEmulation: {
      mobile: false,
      width: 1350,
      height: 940,
      deviceScaleFactor: 1,
      disabled: false,
    },
  },
};
