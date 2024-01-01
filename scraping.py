import asyncio
from pyppeteer import launch

async def main():
    browser = await launch()
    page = await browser.newPage()
    await page.goto('https://tv1.kuronime.vip/')
    await page.type('.search-live', 'one piece')
    await page.click("#submit")
    await page.waitForNavigation()
    # element = await page.querySelector('div.bsx a')
    # title = await page.evaluate('(element) => element.href', element)
    search =  await page.evaluate("""() => {
    let arr = [];
    let element = document.querySelectorAll('div.bsx a');
    element.forEach((el)=>{
                             
        arr.push(el.href);                   
    });
    return arr;
    
                             }
                             """)
    print(search[-1])
    # element = await page.querySelectorAll("span.lchx")
    # p = await page.evaluate("""(element) => element""", element)
   
    await page.screenshot({'path': 'screenshot.png'})
    await browser.close()

asyncio.get_event_loop().run_until_complete(main())