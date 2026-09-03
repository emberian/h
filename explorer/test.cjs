// Headless walk through the guided path, against a running explorer (default http://127.0.0.1:8130).
//
//   NODE_PATH=/Users/ember/tools/playwright/node_modules node test.cjs
//
// load -> start pane visible -> Ask h -> loom shows a labelled root and 4 sample children within 60 s ->
// Compare the models -> samples from at least two servers -> Replay the room -> observatory list and a record
// -> ? help lists the panes -> recent list has the compare. The bar is zero console errors.
// SHOT_DIR=<dir> saves a screenshot per step.
'use strict';
const { chromium } = require('playwright');

const URL = process.env.EXPLORER_URL || 'http://127.0.0.1:8130';
const SHOTS = process.env.SHOT_DIR || '';

(async () => {
  const t0 = Date.now();
  const step = msg => console.log(`${((Date.now() - t0) / 1000).toFixed(1).padStart(5)}s  ${msg}`);
  const browser = await chromium.launch({ channel: 'chrome' });
  const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 } });  // fresh profile: no saved weave
  const page = await ctx.newPage();
  const errors = [];
  page.on('console', m => { if (m.type() === 'error') errors.push('console: ' + m.text()); });
  page.on('pageerror', e => errors.push('pageerror: ' + e.message));
  const shot = async name => { if (SHOTS) await page.screenshot({ path: `${SHOTS}/${name}.png` }); };

  // 1. load: the start pane, with the library and the pane map
  await page.goto(URL);
  await page.waitForSelector('#tab-start.on', { state: 'visible', timeout: 15000 });
  await page.waitForFunction(() => document.querySelectorAll('#start-prompt option').length >= 12, null, { timeout: 15000 });
  step(`start pane: ${await page.locator('#start-prompt option').count()} library options, ${await page.locator('#start-panes li').count()} pane blurbs, ${await page.locator('.start-card').count()} actions`);
  await shot('1-start');

  // 2. Ask h: loom with a labelled root and four answers from the resident
  await page.click('#start-ask');
  await page.waitForSelector('#tab-loom.on', { timeout: 5000 });
  await page.waitForFunction(() => {
    const nodes = [...document.querySelectorAll('#tree .node')];
    const kindOf = n => n.querySelector('.head .kind')?.textContent;
    const root = nodes.find(n => kindOf(n) === 'prompt' && n.querySelector('.head .lib'));
    const kids = nodes.filter(n => kindOf(n) === 'sample' && (n.querySelector('.text')?.textContent || '').trim().length > 0);
    return !!root && kids.length >= 4;
  }, null, { timeout: 60000 });
  const label = await page.locator('#tree .node .head .lib').first().textContent();
  const samples = await page.evaluate(() => [...document.querySelectorAll('#tree .node')].filter(n => n.querySelector('.head .kind')?.textContent === 'sample').map(n => n.querySelector('.text').textContent.replace(/\s+/g, ' ').trim().slice(0, 60)));
  step(`loom: root "${label}", ${samples.length} samples: ${samples.map(s => JSON.stringify(s)).join(' ')}`);
  await page.click('#tree .node .head .kind:text-is("sample") >> xpath=ancestor::div[contains(@class,"node")][1]');
  const nav = await page.locator('#tree .node.active .nav button').count();
  const acts = await page.locator('#tree .node.active .actions button').count();
  const reading = (await page.locator('#reading').textContent()).length;
  step(`selected a sample: ${nav} nav buttons, ${acts} action buttons, ${reading} chars in the reading`);
  if (nav < 4 || acts < 8) throw new Error('selected node is missing its buttons');
  await shot('2-loom');

  // 3. Compare the models: one column per live server
  await page.click('.tabs button[data-tab=start]');
  await page.click('#start-compare');
  await page.waitForSelector('#tab-compare.on', { timeout: 5000 });
  await page.waitForFunction(() => [...document.querySelectorAll('#cmp-cols .col')].filter(c => c.querySelector('.sample')).length >= 2, null, { timeout: 90000 });
  const cols = await page.evaluate(() => [...document.querySelectorAll('#cmp-cols .col')].map(c => `${c.querySelector('h3').textContent}: ${c.querySelectorAll('.sample').length}`));
  step(`compare: ${cols.length} columns; samples so far ${cols.join(' | ')}`);
  await shot('3-compare');

  // 4. Replay the room: the newest day, its latest record open
  await page.click('.tabs button[data-tab=start]');
  await page.click('#start-replay');
  await page.waitForSelector('#tab-observatory.on', { timeout: 5000 });
  await page.waitForFunction(() => document.querySelectorAll('#obs-list table tr').length >= 2 && document.querySelectorAll('#obs-detail .cand').length >= 1, null, { timeout: 30000 });
  step(`observatory: ${await page.inputValue('#obs-date')}, ${(await page.locator('#obs-list table tr').count()) - 1} records, open record has ${await page.locator('#obs-detail .cand').count()} candidates`);
  await shot('4-observatory');

  // 5. the ? help from a pane, and the recent list back on start
  await page.click('#help-btn');
  await page.waitForSelector('#help[open]');
  step(`help: ${await page.locator('#help-panes li').count()} panes, ${await page.locator('#help .keys tr').count()} keys`);
  await page.keyboard.press('Escape');
  await page.click('.tabs button[data-tab=start]');
  step(`recent: ${await page.locator('#start-recent li').count()} entries (${(await page.locator('#start-recent').textContent()).replace(/\s+/g, ' ').trim().slice(0, 100)})`);
  await shot('5-start-again');

  // 6. the library in the loom and in compare fills the box
  await page.click('.tabs button[data-tab=loom]');
  await page.selectOption('#loom-library', 'open-0');
  const rootText = await page.inputValue('#loom-prompt');
  await page.click('.tabs button[data-tab=compare]');
  await page.selectOption('#cmp-library', 'room-9');
  const cmpText = await page.inputValue('#cmp-prompt');
  step(`library: loom root now ${JSON.stringify(rootText.slice(0, 40))}, compare prompt ends ${JSON.stringify(cmpText.slice(-50))}, K=${await page.inputValue('#cmp-k')} max=${await page.inputValue('#cmp-max')}`);
  if (!rootText.startsWith('The lake') || !cmpText.endsWith('h:')) throw new Error('library selection did not fill the boxes');

  await browser.close();
  if (errors.length) { console.log(`FAIL: ${errors.length} console error(s)`); errors.forEach(e => console.log('   ' + e)); process.exit(1); }
  console.log('PASS: guided path complete, zero console errors');
})().catch(e => { console.error('FAIL', e.message || e); process.exit(1); });
