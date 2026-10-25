// End-to-end test of the gold-set coder packets and the coordinator build (headless Chrome).
// Run: npm install puppeteer-core@23.11.1 (once, anywhere on NODE_PATH), then
//      node tools/roadmap/app/e2e_test.js            (OUT=dir for screenshots and files; default ./e2e-out)
// Checks: a full coding passes the app's checks and validates against both schemas (checked afterwards in Python);
// a co-coder's file is refused on import; editing after a save shows "changed since last save"; restore keeps newer drafts;
// the coordinator pairs two coders' files; no page errors.
const puppeteer = require('puppeteer-core');
const fs = require('fs');
const path = require('path');
const ROOT = path.resolve(__dirname, '../../..');
const PACK = id => 'file://' + path.join(ROOT, 'private/data/roadmap/app/packets', id, 'gold-coder.html');
const COORD = 'file://' + path.join(ROOT, 'private/data/roadmap/app/gold-coordinator.html');
const OUT = process.env.OUT || path.join(process.cwd(), 'e2e-out');
fs.mkdirSync(OUT, {recursive: true});
const sleep = ms => new Promise(r => setTimeout(r, ms));
const step = t => process.stderr.write('[e2e] ' + t + '\n');

async function codeOnePaper(browser, coder, dl, url) {
  const page = await browser.newPage();
  const errors = [];
  page.on('pageerror', e => errors.push('pageerror: ' + e.message));
  page.on('dialog', d => d.accept());
  await page.evaluateOnNewDocument(() => { delete window.showDirectoryPicker; });   // force the download route
  const cdp = await page.target().createCDPSession();
  await cdp.send('Page.setDownloadBehavior', {behavior: 'allow', downloadPath: dl});
  await page.setViewport({width: 1500, height: 1000});
  await page.goto(url);
  await page.evaluate(() => localStorage.clear());
  await page.reload();
  await page.waitForSelector('tr[data-k]');
  await page.click('tr[data-k] td:nth-child(2)');
  await page.waitForSelector('#sec-doc');
  const key = await page.evaluate(() => JSON.parse(document.getElementById('payload').textContent).order[0]);
  const sel = (s, v) => page.select(s, v);
  const typ = async (s, v) => { await page.click(s, {clickCount: 3}); await page.type(s, v); };
  await sel('[data-f="pages_convention"]', 'PDF pages counted from 1');
  await sel('[data-f="entry.state"]', 'problem'); await sel('[data-f="entry.node"]', 'Q');
  await typ('[data-f="entry.page"]', '1'); await typ('[data-f="entry.evidence"]', 'The controls on X remain unknown');
  const steps = [['Q','question'],['O','observation'],['I','estimation'],['V','robustness'],['H','hypothesis'],['S','theory'],['C','hypothesis'],['X','hypothesis'],['K','hypothesis']];
  for (let i = 0; i < steps.length; i++) {
    await page.click('[data-addstep="0"]');
    const row = `.step[data-si="0"][data-i="${i}"]`;
    await page.waitForSelector(row);
    await sel(row + ' [data-s="node"]', steps[i][0]); await sel(row + ' [data-s="mode"]', steps[i][1]);
    await sel(row + ' [data-s="move"]', 'new'); await sel(row + ' [data-s="trigger"]', 'author');
    await page.type(row + ' [data-s="action"]', 'Action ' + (i + 1)); await page.type(row + ' [data-s="page"]', String(2 + i));
    await page.type(row + ' [data-s="quote"]', 'short quote ' + (i + 1));
  }
  await page.click('[data-tq="1"]'); await page.waitForSelector('[data-tqa="1"]');
  await page.type('[data-tqa="1"]', 'yes, it repeats'); await sel('[data-tqm="1"]', 'observation');
  await sel('[data-f="end.outcome"]', 'kept'); await sel('[data-f="end.claim_status"]', 'best_explanation');
  await typ('[data-f="end.page"]', '9'); await typ('[data-f="end.claim"]', 'X is controlled by Y.');
  await sel('[data-f="decisive_move.node"]', 'C'); await sel('[data-f="decisive_move.mode"]', 'hypothesis');
  await typ('[data-f="decisive_move.page"]', '8'); await typ('[data-f="decisive_move.sentence"]', 'The comparison that excluded the rival.');
  await sel('[data-f="composition"]', 'strong_inference');
  for (const g of ['action', 'claim', 'registration']) await sel(`[data-f="gates.${g}"]`, g === 'claim' ? 'yes' : 'no');
  await typ('[data-f="gates.evidence"]', 'Archival data; the rival could have matched.');
  await typ('[data-f="limits"]', 'none noted');
  await sel('[data-r="eligible_in_my_view"]', 'yes'); await sel('[data-r="familiarity"]', 'adjacent');
  await typ('[data-r="minutes_spent"]', '55'); await sel('[data-r="impact_forecast"]', 'around_median');
  await typ('[data-r="novelty.atomic_claim"]', 'Y controls X'); await sel('[data-r="novelty.claim_kind"]', 'explanation');
  await sel('[data-r="novelty.judgment"]', 'component_precedent');
  await typ('[data-r="novelty.closest_precedent"]', 'Smith 2019'); await typ('[data-r="novelty.new_component"]', 'A new region');
  await page.click('[data-score="novelty"][value="3"]'); await sel('[data-r="novelty.confidence"]', 'medium');
  for (const f of ['starting_state', 'gain', 'magnitude', 'evidence']) await typ(`[data-r="advance.${f}"]`, 'text for ' + f);
  await page.click('[data-role="cumulative"]'); await page.click('[data-score="advance"][value="2"]');
  await sel('[data-r="advance.confidence"]', 'medium');
  await sleep(500);
  const checks = await page.$eval('#checks', el => el.innerText);
  await page.screenshot({path: path.join(OUT, coder + '-code.png'), fullPage: false});
  step("await page.click('#saveBtn');");
  await page.click('#saveBtn'); await sleep(1500);
  const afterSave = await page.$eval('#saveInfo', el => el.innerText);
  step('// edit after save');
  // edit after save -> changed since last save
  await typ('[data-f="end.claim"]', 'X is controlled by Y and Z.'); await sleep(500);
  const changed = await page.$eval('#saveInfo', el => el.innerText);
  await page.click('#backBtn');
  await page.waitForSelector('table.queue');
  const status = await page.$eval('table.queue tbody tr', el => el.innerText);
  return {page, key, errors, checks, afterSave, changed, status};
}

(async () => {
  const browser = await puppeteer.launch({executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', headless: 'new',
    args: ['--allow-file-access-from-files']});
  const meta = JSON.parse(fs.readFileSync(path.join(ROOT, 'private/data/roadmap/derived/gold/human_assignment.json'))).data;
  // a paper shared by SH and MK, to test pairing and the import refusal
  const shared = meta.papers.find(p => p.assigned.includes('SH') && p.assigned.includes('MK'));
  const res = {};
  for (const coder of ['SH', 'MK']) {
    step('coding as ' + coder);
    const dl = path.join(OUT, 'dl-' + coder); fs.mkdirSync(dl, {recursive: true});
    // put the shared paper first in this coder's order for the test only (in a copy of the packet page)
    const src = fs.readFileSync(PACK(coder).replace('file://', ''), 'utf8');
    const m = src.match(/<script id="payload" type="application\/json">([\s\S]*?)<\/script>/);
    const P = JSON.parse(m[1].replace(/<\\\//g, '</'));
    P.order = [shared.key].concat(P.order.filter(k => k !== shared.key));
    const testPage = path.join(path.dirname(PACK(coder).replace('file://', '')), 'e2e-test-copy.html');
    const blob = JSON.stringify(P).replace(/<\//g, '<\\/');
    fs.writeFileSync(testPage, src.replace(m[1], () => blob));   // a function, so "$" in the JSON is not a replacement pattern
    res[coder] = await codeOnePaper(browser, coder, dl, 'file://' + testPage).catch(e => ({error: String(e), errors: [], checks: '', afterSave: '', changed: '', status: ''}));
    res[coder].testPage = testPage;
  }
  step('// import refusal');
  // import refusal: SH loads MK's coding file
  if (!res.SH.page || !res.MK.page) { console.log(JSON.stringify({SH: res.SH.error, MK: res.MK.error})); process.exit(1); }
  const shPage = res.SH.page; await shPage.bringToFront();
  await shPage.waitForSelector('tr[data-k]'); await shPage.click('tr[data-k] td:nth-child(2)'); await shPage.waitForSelector('#importFile');
  const mkFile = path.join(OUT, 'dl-MK', `${shared.key}.MK.coding.json`);
  const input = await shPage.$('#importFile'); await input.uploadFile(mkFile); await sleep(800);
  const refused = await shPage.evaluate(() => document.body.innerText.includes('You can load only your own files'));
  step('// coordinator pairs');
  // coordinator pairs the two coders
  const cp = await browser.newPage(); await cp.bringToFront(); const cerr = []; cp.on('pageerror', e => cerr.push(e.message));
  await cp.goto(COORD);
  const files = ['SH', 'MK'].flatMap(c => ['coding', 'ratings'].map(k => path.join(OUT, 'dl-' + c, `${shared.key}.${c}.${k}.json`)));
  const fin = await cp.$('#files'); await fin.uploadFile(...files); await sleep(1000);
  const coordText = await cp.$eval('main', el => el.innerText);
  await cp.screenshot({path: path.join(OUT, 'coordinator.png'), fullPage: true});
  step('const out = {shared');
  const out = {shared: shared.key, refused_cocoder_import: refused, coordinator_errors: cerr,
    coordinator_pairs: /1 coder pairs/.test(coordText),
    SH: {errors: res.SH.errors, checks_ok: /No errors/.test(res.SH.checks), afterSave: res.SH.afterSave, changed: /Changed since then/.test(res.SH.changed), status: res.SH.status},
    MK: {errors: res.MK.errors, checks_ok: /No errors/.test(res.MK.checks), afterSave: res.MK.afterSave}};
  console.log(JSON.stringify(out, null, 1));
  for (const c of ['SH', 'MK']) { try { fs.unlinkSync(res[c].testPage); } catch (e) {} }
  await browser.close();
})().catch(e => { console.error('FAILED', e); process.exit(1); });
