// Screen recorder for the experiment-walkthrough films. It drives the real course page with Playwright and
// keeps grabbing screenshots while each "shot" runs, together with where the (drawn) cursor should be.
// scripts/film/walkthrough.py composes the shots into the film: page in a window, cursor, zoom, captions.
//
//   const rec = await Recorder.start({ url, lang, out });
//   await rec.shot({ zh: '…', en: '…', chapter: {zh, en}, zoom: '#lab .lab-side' }, async r => { await r.click(locator); });
//   await rec.finish();
import fs from 'node:fs';
import path from 'node:path';
import { chromium } from '/opt/node-tools/node_modules/playwright/index.mjs';

const VIEW = { width: 1600, height: 900 }, SCALE = 1.2; // screenshots are 1920×1080

export class Recorder {
  static async start({ url, lang, out, storage = {} }) {
    const r = new Recorder();
    r.lang = lang; r.out = out; r.shots = []; r.cursor = { x: VIEW.width * 0.62, y: VIEW.height * 0.55 };
    fs.rmSync(out, { recursive: true, force: true });
    fs.mkdirSync(path.join(out, 'frames'), { recursive: true });
    r.browser = await chromium.launch();
    r.page = await r.browser.newPage({ viewport: VIEW, deviceScaleFactor: SCALE, locale: lang === 'en' ? 'en-US' : 'zh-CN', reducedMotion: 'no-preference' });
    await r.page.addInitScript(s => { for (const [k, v] of Object.entries(s)) localStorage.setItem(k, v); }, { 'learning-clustering:lang': lang, ...storage });
    await r.page.goto(url, { waitUntil: 'networkidle', timeout: 60000 });
    await r.page.addStyleTag({ content: '.lang-hint{display:none!important} *{caret-color:auto}' });
    await r.page.waitForTimeout(800);
    return r;
  }

  t(zh, en) { return this.lang === 'en' ? en : zh; }

  async shot(meta, action = async () => {}, { hold = 0 } = {}) {
    const shot = { index: this.shots.length, caption: { zh: meta.zh, en: meta.en }, chapter: meta.chapter || null, frames: [], cursor: [], zoom: null, hold };
    this.shots.push(shot);
    this.cur = shot;
    this.t0 = Date.now(); this.paused = 0; this.capturing = true;
    shot.cursor.push({ t: 0, x: this.cursor.x * SCALE, y: this.cursor.y * SCALE, kind: 'at' });
    const loop = this.capture(shot);
    try { await action(this); }
    finally {
      await this.page.waitForTimeout(350);
      this.capturing = false;
      await loop;
    }
    // The zoom target is measured once the shot's action is done, so it frames the result.
    if (meta.zoom) shot.zoom = await this.box(meta.zoom, meta.zoomPad ?? 24);
    shot.duration = this.now();
    console.log(`shot ${shot.index}: ${shot.frames.length} frames, ${shot.duration.toFixed(1)} s — ${meta.en || ''}`);
  }

  now() { return (Date.now() - this.t0 - this.paused) / 1000; }

  async capture(shot) {
    while (this.capturing) {
      if (this.pausedSince) { await new Promise(r => setTimeout(r, 30)); continue; }
      const t = this.now();
      const file = `s${String(shot.index).padStart(2, '0')}_${String(shot.frames.length).padStart(4, '0')}.jpg`;
      try {
        const buf = await this.page.screenshot({ type: 'jpeg', quality: 90 });
        if (this.pausedSince) continue;      // a pause began while grabbing: drop the frame
        fs.writeFileSync(path.join(this.out, 'frames', file), buf);
        shot.frames.push({ t, file });
      } catch { /* navigation in progress */ }
    }
  }

  // Time spent here is cut from the film (e.g. waiting for Python to start).
  async offscreen(fn) {
    this.pausedSince = Date.now();
    try { return await fn(); }
    finally { this.paused += Date.now() - this.pausedSince; this.pausedSince = null; }
  }

  async box(target, pad = 24) {
    const loc = typeof target === 'string' ? this.page.locator(target).first() : target;
    const b = await loc.boundingBox();
    if (!b) return null;
    return { x: (b.x - pad) * SCALE, y: (b.y - pad) * SCALE, w: (b.width + 2 * pad) * SCALE, h: (b.height + 2 * pad) * SCALE };
  }

  async moveTo(loc, { glide = 0.55, dx = 0.5, dy = 0.5 } = {}) {
    await loc.scrollIntoViewIfNeeded();
    const b = await loc.boundingBox();
    const x = b.x + b.width * dx, y = b.y + b.height * dy;
    this.cur.cursor.push({ t: this.now(), x: x * SCALE, y: y * SCALE, kind: 'move', glide });
    await this.page.waitForTimeout(glide * 1000 + 120);
    this.cursor = { x, y };
    await this.page.mouse.move(x, y);
    return { x, y };
  }

  async click(loc, opts = {}) {
    await this.moveTo(loc, opts);
    this.cur.cursor.push({ t: this.now(), x: this.cursor.x * SCALE, y: this.cursor.y * SCALE, kind: 'click' });
    await this.page.mouse.click(this.cursor.x, this.cursor.y);
    await this.page.waitForTimeout(opts.after ?? 500);
  }

  async choose(selectLoc, value, opts = {}) {
    await this.moveTo(selectLoc, opts);
    this.cur.cursor.push({ t: this.now(), x: this.cursor.x * SCALE, y: this.cursor.y * SCALE, kind: 'click' });
    await selectLoc.selectOption(value);
    await this.page.waitForTimeout(opts.after ?? 700);
  }

  async type(text, { delay = 45 } = {}) {
    for (const line of text.split('\n').map((l, i) => [l, i])) {
      const [s, i] = line;
      if (i > 0) { await this.page.keyboard.press('Escape'); await this.page.keyboard.press('Enter'); await this.page.waitForTimeout(120); }
      const dedent = s.match(/^<+/)?.[0].length || 0;
      for (let k = 0; k < dedent; k++) await this.page.keyboard.press('Backspace');
      await this.page.keyboard.type(s.slice(dedent), { delay });
    }
    await this.page.keyboard.press('Escape');
  }

  async scrollTo(target, { offset = 90, duration = 900 } = {}) {
    const y = await this.page.locator(target).first().evaluate((el, off) => el.getBoundingClientRect().top + scrollY - off, offset);
    await this.page.evaluate(([y, d]) => new Promise(res => {
      const y0 = scrollY, t0 = performance.now();
      const step = now => { const k = Math.min(1, (now - t0) / d), e = k < 0.5 ? 2 * k * k : 1 - (-2 * k + 2) ** 2 / 2; scrollTo(0, y0 + (y - y0) * e); k < 1 ? requestAnimationFrame(step) : res(); };
      requestAnimationFrame(step);
    }), [y, duration]);
    await this.page.waitForTimeout(250);
  }

  wait(ms) { return this.page.waitForTimeout(ms); }

  async finish(meta = {}) {
    fs.writeFileSync(path.join(this.out, 'timeline.json'), JSON.stringify({ lang: this.lang, size: [VIEW.width * SCALE, VIEW.height * SCALE], ...meta, shots: this.shots }, null, 1));
    await this.browser.close();
  }
}
