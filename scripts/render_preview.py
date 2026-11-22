"""Offline browser screenshot for the *look* of the profile, not published to GitHub."""
from pathlib import Path
import asyncio
import base64
import mistune
from playwright.async_api import async_playwright

ROOT=Path(__file__).resolve().parents[1]
readme=(ROOT/'README.md').read_text(encoding='utf-8')
renderer=mistune.create_markdown(escape=False,plugins=['table','strikethrough'])
body=renderer(readme)
html=f'''<!DOCTYPE html><html><head><meta charset="utf-8"/>
<style>
  :root {{color-scheme:dark}}
  body {{ margin:0; background:#0d1117; color:#e6edf3; font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Arial,sans-serif; }}
  .mast {{background:#010409;border-bottom:1px solid #30363d;height:58px;display:flex;align-items:center;padding:0 5vw;gap:20px;color:#c9d1d9;font-weight:600;font-size:14px}}
  .mast .logo {{font-family:monospace;color:#e6edf3;font-size:24px;letter-spacing:-4px}}
  .pill {{font-size:11px;border:1px solid #30363d;padding:4px 9px;border-radius:25px;font-weight:400}}
  .side {{color:#8b949e;font-size:12px}}
  .main {{max-width:930px;margin:38px auto 110px;}}
  .label {{font-size:12px;color:#8b949e;margin:0 0 12px 1px;}}
  .markdown-body {{border:1px solid #30363d;border-radius:6px;padding:30px 42px;line-height:1.65; overflow:hidden; font-size:15px}}
  .markdown-body h1 {{font-size:2em;line-height:1.25;margin:18px 0 14px;border-bottom:none;color:#f0f6fc}}
  .markdown-body h3 {{font-size:1.35em;line-height:1.35;border-bottom:1px solid #30363d;padding-bottom:8px;margin:40px 0 16px;color:#f0f6fc}}
  .markdown-body p {{margin:14px 0}}
  .markdown-body a {{color:#58a6ff;text-decoration:none}}
  .markdown-body a:hover {{text-decoration:underline}}
  .markdown-body hr {{border:0;border-top:1px solid #30363d;margin:27px 0}}
  .markdown-body img {{max-width:100%;height:auto;vertical-align:middle}}
  .markdown-body img[align="right"] {{margin:0 0 18px 24px}}
  .markdown-body table {{border-collapse:collapse;width:100%;margin:20px 0;display:table}}
  .markdown-body td,.markdown-body th {{border:1px solid #30363d;padding:9px 13px}}
  .markdown-body tr:nth-child(2n){{background:#161b22}}
  .markdown-body th {{font-weight:650}}
  .markdown-body code {{font:12px ui-monospace,SFMono-Regular,Consolas,monospace}}
  .markdown-body pre {{background:#161b22;border-radius:6px;padding:16px;overflow:auto}}
  .markdown-body pre code {{font-size:13px;line-height:1.7;color:#c9d1d9}}
  .markdown-body details {{border-radius:6px;border:1px solid #30363d;padding:11px 15px}}
  .markdown-body summary {{cursor:pointer}}
  .markdown-body li {{margin:6px 0}}
  .markdown-body sub {{font-size:11px;color:#8b949e}}
</style></head><body>
<div class="mast"><span class="logo">&lt;&gt;</span><span>RITU940 / RITU940</span><span class="pill">Public</span><span class="side">Code &nbsp;&nbsp; Issues &nbsp;&nbsp; Pull requests &nbsp;&nbsp; Actions</span></div>
<div class="main"><p class="label">RITU940 / README.md</p><main class="markdown-body">{body}</main></div>
</body></html>'''
(ROOT/'profile-preview.html').write_text(html,encoding='utf-8')
for fn, mime in [('hero-ritu.gif','image/gif'), ('late-night-coding.gif','image/gif'), ('characters/cat.gif','image/gif'), ('characters/robot.gif','image/gif'), ('characters/oscilloscope.gif','image/gif'), ('pull-requests.svg','image/svg+xml'), ('toolbox-stickers.svg','image/svg+xml')]:
    path=(ROOT/'preview'/'pr-graph-SAMPLE.svg') if fn=='pull-requests.svg' else (ROOT/'assets'/fn)
    blob=base64.b64encode(path.read_bytes()).decode('ascii')
    html=html.replace('src="assets/'+fn+'"', 'src="data:'+mime+';base64,'+blob+'"')
async def run():
    async with async_playwright() as p:
        browser=await p.chromium.launch(headless=True, executable_path='/usr/bin/chromium',args=['--no-sandbox','--allow-file-access-from-files'])
        page=await browser.new_page(viewport={'width':1100,'height':900},device_scale_factor=1)
        await page.set_content(html, wait_until='load')
        await page.wait_for_timeout(400)
        await page.screenshot(path=str(ROOT/'preview'/'Full_Profile_Preview.png'),full_page=True,animations='disabled')
        await browser.close()
asyncio.run(run())
