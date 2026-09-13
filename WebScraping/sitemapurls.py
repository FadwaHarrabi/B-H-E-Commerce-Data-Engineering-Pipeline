import requests
from bs4 import BeautifulSoup
import asyncio 
from camoufox.async_api import AsyncCamoufox
from parsel import Selector
url="https://www.bhphotovideo.com/SiteMapIndex.xml"

async def fetchpage(page,url):
    response=await page.goto(url,timeout=60000,wait_until="domcontentloaded")
    print(response.status)
    content=await page.content()
    html=Selector(text=content)
    print("HTML length:", len(content))
    return html

async def get_urls_lastmodif(page,url):
    sel= await fetchpage(page,url)
    urls=sel.xpath("//sitemap/loc/text()").getall()
    last_modifs=sel.xpath("//sitemap/lastmod/text()").getall()
    for url,date in zip(urls,last_modifs):
        print("url",url,"last modif",date)

    
async def main():
    async with AsyncCamoufox (headless=True) as browser:
        page=await browser.new_page()
        await get_urls_lastmodif(page,url=url)


if __name__=="__main__":
    asyncio.run(main())