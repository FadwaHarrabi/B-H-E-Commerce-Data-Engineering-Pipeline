import asyncio
from camoufox.async_api import AsyncCamoufox
from parsel import Selector
import json
from datetime import datetime,timezone
import logging
scraped_at=datetime.now(timezone.utc).isoformat()
logger=logging.getLogger(__name__)
BASE_URL= "https://www.bhphotovideo.com/"
NUM_WORKERS = 3



department=[]
categories=[]
subcategories_group=[]
subsubcategories_group=[]
category_filters = []
products=[]


async def worker(worker_id,semaphore,queue ):
    async with AsyncCamoufox(headless=True, humanize=True, window=(1280, 720)) as browser:
        page = await browser.new_page()

        while True:
            job = await queue.get()

            try:
                url = job["url"]
                level = job["level"]
                parent_id = job["parent_id"]

                print(
                    f"\nWorker {worker_id} GOT JOB\n"
                    f"Level: {level}\n"
                    f"URL: {url}"
                )

                async with semaphore:

                    print(
                        f"Worker {worker_id} PROCESSING: {url}"
                    )

                    if level == "Department":

                        await get_categories(
                            page,
                            url,
                            parent_id,
                            queue
                        )

                    elif level == "Category1":

                        await get_sub_category_group(
                            page,
                            url,
                            parent_id,
                            queue
                        )

                    elif level == "Category2":

                        await get_all_products(
                            page,
                            url,
                            category_code=parent_id
                        )

                    elif level == "SubCategory1":

                        await get_sub_sub_category_group(
                            page,
                            url,
                            parent_id,
                            queue
                        )

                    elif level == "SubCategory2":

                        await get_all_products(
                            page,
                            url,
                            subcategory_code=parent_id
                        )

                    elif level == "SubSubCategory":

                        await get_all_products(
                            page,
                            url,
                            subsubcategory_code=parent_id
                        )

                    print(
                        f"Worker {worker_id} FINISHED: {url}"
                    )

            except Exception as e:

                print(
                    f"\n❌ WORKER {worker_id} ERROR"
                )
                print(f"URL: {job.get('url')}")
                print(f"LEVEL: {job.get('level')}")
                print(f"ERROR: {repr(e)}")

            finally:
                queue.task_done()

async def fetch_page(page, url):

    print(f"\nNavigating to: {url}")

    try:
        response = await page.goto(
            url,
            timeout=60000,
            wait_until="domcontentloaded"
        )

        status = response.status if response else None

        print(f"STATUS: {status}")
        print(f"URL: {page.url}")
        print(f"TITLE: {await page.title()}")

        # Give JS a little time
        await page.wait_for_timeout(2000)

        title = await page.title()

        if "Just a moment" in title:
            print("Cloudflare challenge detected.")

            for i in range(15):
                await page.wait_for_timeout(1000)

                title = await page.title()

                print(
                    f"Cloudflare wait {i + 1}s | "
                    f"title={title}"
                )

                if "Just a moment" not in title:
                    break

        htmlcontent = await page.content()

        print(
            f"Finished: {page.url} | "
            f"title={await page.title()} | "
            f"html={len(htmlcontent)} chars"
        )

        return Selector(text=htmlcontent)

    except Exception as e:
        print(f"ERROR loading {url}: {e}")
        raise

async def get_department(page, url, queue):

    sel = await fetch_page(page, url)

    titles_list = sel.xpath(
        "//a[@class='navItemLink_aYw0EFMa2c']/span/text()"
    ).getall()

    urls_list = sel.xpath(
        "//a[@class='navItemLink_aYw0EFMa2c']/@href"
    ).getall()

    print("\n========== DEPARTMENT DEBUG ==========")
    print("Titles found:", len(titles_list))
    print("URLs found:", len(urls_list))
    print("Titles:", titles_list)
    print("URLs:", urls_list)

    titles_list = [
        title.strip()
        for title in titles_list
        if title.strip()
    ]

    urls_list = [
        url.strip()
        for url in urls_list
        if url.strip()
    ]

    print("After cleaning:")
    print("Titles:", len(titles_list))
    print("URLs:", len(urls_list))

    scraped_at = datetime.now(timezone.utc).isoformat()

    for title, urls in zip(titles_list, urls_list):

        DepartmentCode = f"D00{len(department) + 1}"

        full_url = (
            urls
            if urls.startswith("http")
            else f"https://www.bhphotovideo.com{urls}"
        )

        department.append({
            "Code": DepartmentCode,
            "DepartmentName": title,
            "url": urls,
            "ScrapedAt": scraped_at
        })

        print(
            f"PUTTING JOB → {DepartmentCode} | "
            f"{title} | {full_url}"
        )

        await queue.put({
            "url": full_url,
            "level": "Department",
            "parent_id": DepartmentCode
        })

    print(
        f"========== {queue.qsize()} JOBS IN QUEUE ==========\n"
    )
async def get_categories(page, url,DepartmentCode,queue):
    sel = await fetch_page(page, url)
    subcategories = sel.css("h2[data-selenium='categoryGroupHeaderName']::text").getall()
    products=sel.css("span[data-selenium='categoryGroupText']::text").getall()
    products_url=sel.css("a[data-selenium='categoryGroupLink']::attr(href)").getall()
    subcategory = [sub.strip() for sub in subcategories if sub.strip()]
    product = [pr.strip() for pr in products if pr.strip()]
    product_url=[url.strip() for url in products_url if url.strip()]
    scraped_at=datetime.now(timezone.utc).isoformat()
    for sub,pr,ur in zip(subcategory,product,product_url):
        CategoriesCode=f"{'C00'}{len(categories) + 1}"
        categories.append({ "Code": CategoriesCode,'Category':sub,'SubCategory':pr,'url':ur,'DepartmentCode':DepartmentCode,"ScrapedAt":scraped_at})
        full_product_url=ur if ur.startswith('http') else f"https://www.bhphotovideo.com{ur}"
        if 'browse' in full_product_url:
            # await get_sub_category_group(page,full_product_url,CategoriesCode)
            await queue.put({"url": full_product_url, "level": "Category1", "parent_id": CategoriesCode})
        elif 'buy' in full_product_url:
            # await get_all_products(page,full_product_url,category_code=CategoriesCode)
            await queue.put({"url": full_product_url, "level": "Category2", "parent_id": CategoriesCode}) 

async def get_sub_category_group(page,url,CategoriesCode,queue):
    sel=await fetch_page(page,url)
    url_list=sel.css("a[data-selenium='categoryGroupLink']::attr(href)").getall()
    name_categories_group=sel.css("span[data-selenium='categoryGroupText']::text").getall()
    urls=[ur.strip() for ur in url_list if ur.strip()]
    name=[name.strip() for name in name_categories_group  if name.strip()]
    scraped_at=datetime.now(timezone.utc).isoformat()
    for nm,ur in zip(name,urls):
        SubcategoriesgroupCode=f"{'S00'}{len(subcategories_group) + 1}"
        subcategories_group.append({"Code": SubcategoriesgroupCode,"name":nm,"url":ur,'CategoriesCode':CategoriesCode,"ScrapedAt":scraped_at})
        full_ur=ur if ur.startswith('http') else f"https://www.bhphotovideo.com{ur}"
        if 'browse' in full_ur:
            await queue.put({"url": full_ur, "level": "SubCategory1", "parent_id": SubcategoriesgroupCode})
            # await get_sub_sub_category_group(page,full_ur,SubcategoriesgroupCode)
        # elif 'buy' in full_ur:
        #     await get_all_products(page,full_ur,subcategory_code=SubcategoriesgroupCode)
        elif 'buy' in full_ur:
            # await get_all_products(page,full_ur,subcategory_code=SubcategoriesgroupCode)
            await queue.put({"url": full_ur, "level": "SubCategory2", "parent_id": SubcategoriesgroupCode})
async def get_sub_sub_category_group(page,url,SubcategoriesgroupCode,queue):
    sel=await fetch_page(page,url)
    names=sel.css("span[data-selenium='categoryGroupText']::text").getall()
    links=sel.css("a[data-selenium='categoryGroupLink']::attr(href)").getall()
    name=[nm.strip() for nm in names if nm.strip()]
    link=[lnk.strip() for lnk in links if lnk .strip()]
    scraped_at=datetime.now(timezone.utc).isoformat()
    for n,lk in zip(name,link):
        subsubcategory_Code=f"{'SC00'}{len(subsubcategories_group) +1}"
        subsubcategories_group.append({ "Code": subsubcategory_Code,"name":n,"url":lk,'SubcategoriesCode':SubcategoriesgroupCode,"ScrapedAt":scraped_at})

        full_url=lk if lk.startswith('http') else f"https://www.bhphotovideo.com{lk}"
        # await get_all_products(page,full_url,subsubcategory_code=subsubcategory_Code)
        await queue.put({"url": full_url, "level": "SubSubCategory", "parent_id": subsubcategory_Code})
            
def clean_list(items):
    return [item.strip() for item in items if item.strip()]

async def get_products(page,url, category_code=None,subcategory_code=None,subsubcategory_code=None):
    sel=await fetch_page(page,url)
    filter_name=sel.css("h3[data-selenium='collapseContainerTitle']::text").getall()
    options=sel.css("label[data-selenium='checkBoxLabel'] span::text").getall()
    product_img=sel.css("img[data-selenium='miniProductPageImg']::attr(src)").getall()
    product_name=sel.css("span[data-selenium='miniProductPageProductName']::text").getall()
    product_reference=sel.css("div[data-selenium='miniProductPageProductSkuInfo']").xpath("string(.)").getall()
    product_price1=sel.css("span[data-selenium='uppedDecimalPriceFirst']::text").getall()
    product_price2=sel.css("sup[data-selenium='uppedDecimalPriceSecond']::text").getall()
    initial_price=sel.css("del[data-selenium='strikethroughPrice'] span::text").getall()
    saved_price=sel.css("div[data-selenium='defaultSaving'] span::text").getall()
    stock_status=sel.css("span[data-selenium='stockStatus']::text").getall()
    nb_reviews=sel.css("span[data-selenium='miniProductPageProductReviews']::text").getall()
    product_key_features=sel.css("li[data-selenium='miniProductPageSellingPointsListItem']").xpath("string(.)").getall()
    # page_nb=sel.css("a[data-selenium='listingPagingLink']::text").getall()
    # page_link=sel.css("a[data-selenium='listingPagingLink']::attr(href)").getall()
    filter_name=clean_list(filter_name)
    options=clean_list(options)
    product_img=clean_list(product_img)
    product_name=clean_list(product_name)
    product_reference=clean_list(product_reference)
    product_price1=clean_list(product_price1)
    product_price2=clean_list(product_price2)
    initial_price=clean_list(initial_price)
    saved_price=clean_list(saved_price)
    stock_status=clean_list(stock_status)
    nb_reviews=clean_list(nb_reviews)
    product_key_features=clean_list(product_key_features)
    scraped_at=datetime.now(timezone.utc).isoformat()
    for filter ,option in zip(filter_name,options):
        FiltersCode=f"{'F00'}{len(category_filters)+1}"
        category_filters.append({"Code":FiltersCode,"category_code": category_code,"subcategory_code": subcategory_code,"subsubcategory_code": subsubcategory_code,"filter":filter,"options":option,"ScrapedAt":scraped_at})
    for (
        img,
        name,
        reference,
        price1,
        price2,
        initial,
        saved,
        stock,
        reviews,
        key_features
    ) in zip(
        product_img,
        product_name,
        product_reference,
        product_price1,
        product_price2,
        initial_price,
        saved_price,
        stock_status,
        nb_reviews,
        product_key_features
    ):
        ProductCode=f"{'P00'}{len(products) + 1}"
        products.append({
            "Code": ProductCode,
            "category_id": category_code,
            "subcategory_id": subcategory_code,
            "subsubcategory_id": subsubcategory_code,
            "image": img,
            "name": name,
            "reference": reference,
            "price": f"{price1}.{price2}",
            "initial_price": initial,
            "saved_price": saved,
            "stock_status": stock,
            "reviews": reviews,
            "key_features": key_features,
            "ScrapedAt":scraped_at
        })
    return sel


async def get_all_products(page,url,category_code=None,subcategory_code=None,subsubcategory_code=None):
    visited_urls = set()
    page_number = 1

    while url:

        print("\n" + "=" * 80)
        print(f"PRODUCT PAGE {page_number}")
        print(f"URL: {url}")
        print("=" * 80)

        # Prevent infinite pagination
        if url in visited_urls:
            print("URL ALREADY VISITED - STOPPING")
            break

        visited_urls.add(url)

        sel = await get_products(
            page,
            url,
            category_code,
            subcategory_code,
            subsubcategory_code
        )

        next_url = sel.css(
            "a[data-selenium='listingPagingPageNext']::attr(href)"
        ).get()

        print(f"RAW NEXT URL: {next_url}")

        if not next_url:
            print("No next page. Finished.")
            break

        next_url = next_url.strip()

        if not next_url.startswith("http"):
            next_url = BASE_URL.rstrip("/") + next_url

        print(f"NEXT URL: {next_url}")

        # Prevent same-page loop
        if next_url == url:
            print("NEXT URL IS SAME AS CURRENT URL")
            break

        url = next_url
        page_number += 1
async def main():
    queue = asyncio.Queue()
    semaphore = asyncio.Semaphore(NUM_WORKERS)

    tasks = [
        asyncio.create_task(worker(i, semaphore, queue))
        for i in range(NUM_WORKERS)
    ]

    # Need one throwaway page just to fetch the department list
    async with AsyncCamoufox(headless=True) as browser:
        page = await browser.new_page()
        await get_department(page, BASE_URL, queue)

    await queue.join()

    for task in tasks:
        task.cancel()
    with open ('/opt/airflow/Data/department.json','w',encoding='utf-8') as f:
            json.dump(department,f,ensure_ascii=False,indent=4)
    with open('/opt/airflow/Data/categories.json','w',encoding='utf-8') as f:
        json.dump(categories,f,ensure_ascii=False,indent=4)
    with open('/opt/airflow/Data/subcategories_group.json','w',encoding='utf-8') as f:
        json.dump(subcategories_group,f,ensure_ascii=False,indent=4)
    with open('/opt/airflow/Data/subsubcategory_group.json','w',encoding='utf-8') as f:
        json.dump(subsubcategories_group,f,ensure_ascii=False,indent=4)
    with open('/opt/airflow/Data/filters.json','w',encoding='utf-8') as f:
        json.dump(category_filters,f,ensure_ascii=False,indent=4)
    with open('/opt/airflow/Data/products.json','w',encoding='utf-8') as f:
        json.dump(products,f,ensure_ascii=False,indent=4)
# if __name__=="__main__":
#     asyncio.run(main())