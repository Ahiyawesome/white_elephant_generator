import asyncio
import aiohttp
import random
from bs4 import BeautifulSoup


HEADERS = {     # Using mobile headers because Amazon automatically detects the bot and hides the price
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Referer': 'https://www.amazon.com/',
}

async def fetch_url(session, url):
    async with session.get(url, headers=HEADERS) as response:
        return await response.text()
    

async def extract_data(ls):
    items = []
    soup = BeautifulSoup(ls, 'html.parser')

    products = soup.find_all('div', {'role': 'listitem'})

    for product in products:
        title_tag = product.select_one('a h2 span')
        title = title_tag.get_text().strip() if title_tag else "No Title"

        price_tag = product.select_one('.a-price .a-offscreen')
        price = price_tag.get_text().strip() if price_tag else "N/A"

        item_tuple = (title, price)
        items.append(item_tuple)

    return items
    
async def main():
    tasks = []
    async with aiohttp.ClientSession() as session:
        for page in range (1,5):
            url = f"https://www.amazon.com/s?k=white+elephant+gifts&page={page}"
            tasks.append(fetch_url(session, url))
        
        print("Fetching data...")

        results = await asyncio.gather(*tasks)
    
    new_tasks = []

    for result in results:
        new_tasks.append(extract_data(result))

    extractor_results = await asyncio.gather(*new_tasks)   # list of [page numbers] lists of tuples (item_name, price)
    
    merged_results = []
    for ls in extractor_results:
        merged_results += ls        # makes it into one list of tuples

    n = len(merged_results)
    s = set()
    for _ in range(5):  # 5 random items
        randinx = random.randint(0, n-1)
        while (randinx in s):
            randinx = random.randint(0, n-1)
        s.add(randinx)
        print(f"Item: {merged_results[randinx][0]}, Price: {merged_results[randinx][1]}")
        print("\n\n")


asyncio.run(main())