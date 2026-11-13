// Renders the share card, schema logo and touch icon from HTML using the site's own fonts.
//   node tools/make_images.js      (then: python3 tools/make_favicon.py)
const { chromium } = require('playwright');
const path = require('path');
const fonts = 'file://' + path.resolve(__dirname, '../src/static/fonts');
const OCT = '<svg viewBox="0 0 200 200"><polygon points="58.58,0 141.42,0 200,58.58 200,141.42 141.42,200 58.58,200 0,141.42 0,58.58" fill="#C8102E"/></svg>';
const base = `<style>
@font-face{font-family:Anton;src:url(${fonts}/anton-400.woff2)}
@font-face{font-family:BC;src:url(${fonts}/barlow-condensed-700.woff2);font-weight:700}
*{margin:0;box-sizing:border-box}body{background:#0B0B0C;color:#F4F3EF}
.mesh{background-image:repeating-linear-gradient(45deg,rgba(244,243,239,.06) 0 2px,transparent 2px 24px),repeating-linear-gradient(-45deg,rgba(244,243,239,.06) 0 2px,transparent 2px 24px)}
</style>`;
const og = `${base}<div class="mesh" style="width:1200px;height:630px;display:flex;align-items:center;gap:64px;padding:0 84px">
 <div style="width:300px;flex:none">${OCT}</div>
 <div style="display:grid;gap:22px">
  <div style="font:700 26px BC;letter-spacing:.24em;color:#F0484F;text-transform:uppercase">Octagon Defense · Contract Protection</div>
  <div style="font:400 104px/0.92 Anton;text-transform:uppercase">Trained to fight.<br><span style="color:#F0484F">Paid not to.</span></div>
  <div style="font:700 28px BC;letter-spacing:.3em;color:#ABAAA6;text-transform:uppercase">Lubbock · Houston · DFW</div>
 </div></div>`;
const logo = `${base}<div style="width:600px;height:600px;background:#fff;display:grid;place-items:center;align-content:center;gap:28px">
 <div style="width:250px">${OCT}</div>
 <div style="font:400 72px/0.95 Anton;color:#0B0B0C;text-transform:uppercase;text-align:center">Octagon<br>Defense</div></div>`;
const touch = `${base}<div style="width:180px;height:180px;background:#0B0B0C;display:grid;place-items:center"><div style="width:128px">${OCT}</div></div>`;
(async () => {
  const b = await chromium.launch();
  const out = path.resolve(__dirname, '../src/static/img');
  for (const [html, w, h, file, type] of [[og, 1200, 630, 'og-octagon-defense.jpg', 'jpeg'], [logo, 600, 600, 'octagon-defense-logo.png', 'png'], [touch, 180, 180, 'apple-touch-icon.png', 'png']]) {
    const p = await b.newPage({ viewport: { width: w, height: h } });
    await p.setContent(html, { waitUntil: 'load' });
    await p.evaluate(() => document.fonts.ready);
    await p.screenshot({ path: path.join(out, file), type, ...(type === 'jpeg' ? { quality: 86 } : {}) });
    console.log(file);
  }
  await b.close();
})();
