import asyncio, json
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={'width':390,'height':780})
        errs=[]
        pg.on('pageerror', lambda e: errs.append(str(e)))
        async def route(r):
            u=r.request.url
            if 'wikipedia.org/api/rest_v1' in u:
                await r.fulfill(status=200, content_type='application/json', headers={'access-control-allow-origin':'*'},
                  body=json.dumps({'extract':'仙台城は、宮城県仙台市青葉区にある城。伊達政宗が築いた。別名は青葉城。城跡は国の史跡。石垣が現存する。現在は公園として整備されている。','content_urls':{'desktop':{'page':'https://ja.wikipedia.org/wiki/x'}}}))
            elif 'wikipedia.org/w/api.php' in u:
                await r.fulfill(status=200, content_type='application/json', headers={'access-control-allow-origin':'*'}, body='{"query":{"geosearch":[]}}')
            elif u.startswith('file:'):
                await r.continue_()
            else:
                await r.abort()
        await pg.route('**/*', route)
        await pg.goto('file:///home/claude/proto/sling-spot-ar-prototype.html')
        await pg.click('#bDemo')
        # 方位を仙台城へ
        h = await pg.evaluate("__geo.bearing(38.2601,140.8824,38.2514,140.8566)")
        await pg.evaluate(f"(()=>{{S.heading={h};}})()")
        await pg.mouse.move(195,390); await pg.mouse.down(); await pg.wait_for_timeout(450)
        st1 = await pg.evaluate("[S.state,S.sel&&S.sel.name,S.cand.map(c=>c.name)]")
        for y in range(400,640,20):
            await pg.mouse.move(195,y); await pg.wait_for_timeout(15)
        st2 = await pg.evaluate("[S.state,Math.round(S.pull),S.armed]")
        await pg.screenshot(path='/home/claude/proto/s1_pull.png')
        await pg.mouse.up()
        await pg.wait_for_timeout(500)
        st3 = await pg.evaluate("S.state")
        await pg.wait_for_timeout(5500)
        st4 = await pg.evaluate("[S.state,S.cards.length,S.cardIdx,S.debug.mapError||null]")
        await pg.wait_for_timeout(9000)
        st5 = await pg.evaluate("[S.cardIdx,S.orbitFrac]")
        await pg.screenshot(path='/home/claude/proto/s2_orbit.png')
        await pg.click('#bBack'); st6 = await pg.evaluate("S.state")
        # 短い引きはキャンセルされるか
        await pg.mouse.move(195,390); await pg.mouse.down(); await pg.wait_for_timeout(450)
        await pg.mouse.move(195,430); await pg.mouse.up()
        st7 = await pg.evaluate("S.state")
        # 方向違いはロックされない
        await pg.evaluate("S.heading=(S.heading+120)%360")
        await pg.mouse.move(195,390); await pg.mouse.down(); await pg.wait_for_timeout(450); await pg.mouse.up()
        st8 = await pg.evaluate("S.state")
        print(st1,st2,st3,st4,st5,st6,st7,st8,errs)
        await b.close()
asyncio.run(main())
