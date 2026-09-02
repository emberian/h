// check_site.mjs — load the site headless and wait for the ghost to murmur.
//
//   cd site && python3 -m http.server 8000 &
//   NODE_PATH=/opt/homebrew/lib/node_modules/playwriter/node_modules \
//     node export/check_site.mjs [http://localhost:8000/] [timeout-seconds]
//
// Prints every console message, page error and failed request, the worker's ready/device
// message, and the first fragments the ghost produced. Exit code 0 only if the model loaded
// and at least one fragment arrived with no console errors, page errors, or failed requests.
import { createRequire } from "node:module";
import os from "node:os";
import path from "node:path";
const require = createRequire(import.meta.url);
const { chromium } = require("playwright-core");

const url = process.argv[2] || "http://localhost:8000/";
const timeoutS = Number(process.argv[3] || 600);
const exe = process.env.CHROMIUM || path.join(os.homedir(),
  "Library/Caches/ms-playwright/chromium-1223/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing");

const browser = await chromium.launch({
  executablePath: exe, headless: true,
  args: ["--enable-unsafe-webgpu", "--enable-features=Vulkan", "--use-angle=swiftshader", "--autoplay-policy=no-user-gesture-required"],
});
const page = await browser.newPage({ viewport: { width: 1400, height: 900 } });
const errors = [], failed = [], logs = [];
page.on("console", (m) => { const t = `[console.${m.type()}] ${m.text()}`; logs.push(t); console.log(t); if (m.type() === "error") errors.push(t); });
page.on("pageerror", (e) => { const t = `[pageerror] ${e.message}`; errors.push(t); console.log(t); });
page.on("requestfailed", (r) => { const t = `[requestfailed] ${r.url()} ${r.failure()?.errorText}`; failed.push(t); console.log(t); });
page.on("response", (r) => { if (r.status() >= 400) { const t = `[http ${r.status()}] ${r.url()}`; failed.push(t); console.log(t); } });

// Tap the worker <-> page traffic: ghost.js owns the worker, so listen on the page side.
await page.addInitScript(() => {
  window.__ghost = { ready: null, fragments: [], progress: {}, notes: [] };
  const OrigWorker = window.Worker;
  window.Worker = class extends OrigWorker {
    constructor(...a) {
      super(...a);
      this.addEventListener("message", (e) => {
        const m = e.data || {};
        if (m.type === "ready") window.__ghost.ready = m.device;
        else if (m.type === "unavailable") window.__ghost.ready = "unavailable: " + m.reason;
        else if (m.type === "note") window.__ghost.notes.push(m.text);
        else if (m.type === "progress") window.__ghost.progress[m.file] = m.progress;
        else if (m.type === "done" && m.text) window.__ghost.fragments.push(m.text);
      });
    }
  };
});

const t0 = Date.now();
await page.goto(url, { waitUntil: "load" });
console.log(`[check] loaded ${url}`);
let state = null;
while ((Date.now() - t0) / 1000 < timeoutS) {
  state = await page.evaluate(() => window.__ghost);
  if (state.ready && !String(state.ready).startsWith("unavailable") && state.fragments.length >= 2) break;
  if (state.ready && String(state.ready).startsWith("unavailable")) break;
  await page.waitForTimeout(2000);
}
const dt = ((Date.now() - t0) / 1000).toFixed(1);
console.log(`[check] after ${dt}s: device=${state?.ready} notes=${JSON.stringify(state?.notes)} files=${JSON.stringify(Object.keys(state?.progress || {}))}`);
for (const f of state?.fragments || []) console.log(`[fragment] ${JSON.stringify(f)}`);
await page.screenshot({ path: process.env.SHOT || "/tmp/h-site-check.png" });
await browser.close();
const ok = state?.ready && !String(state.ready).startsWith("unavailable") && (state.fragments.length > 0) && errors.length === 0 && failed.length === 0;
console.log(`[check] ${ok ? "OK" : "FAIL"}: errors=${errors.length} failedRequests=${failed.length} fragments=${state?.fragments?.length ?? 0}`);
process.exit(ok ? 0 : 1);
