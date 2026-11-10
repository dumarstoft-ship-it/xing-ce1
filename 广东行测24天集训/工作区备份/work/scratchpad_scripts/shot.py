import sys, asyncio
from playwright.async_api import async_playwright
async def main(path, out, w=390, h=1400):
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(viewport={'width': w, 'height': h})
        await pg.goto('file://' + path); await pg.screenshot(path=out, full_page=False); await b.close()
asyncio.run(main(sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 390))
