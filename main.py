import asyncio
from concurrent.futures import ThreadPoolExecutor
import logging
import csv

from probe import run
from trim import trim

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s | %(asctime)s | %(filename)s | %(message)s"
)

MAX_WORKERS = 100

values = {
    "success": {},
    "failure": []
}

async def scrape(urls) -> str:
    for url in urls:
        logging.info(f"Initializing Scraping for: {url}")
        html_file_path = await run(url)
        if not html_file_path:
            values["failure"].append(url)
            logging.error(f"Scraping Failed for: {url}")
            continue
        logging.info(f"Scraping Successful for: {url}")
        values["success"][url] = html_file_path

async def main(urls):
    """ Main Function to initialize the project"""
    urlcount = len(urls)
    logging.info(f"Total Urls to be Scraped: {urlcount}")
    max_attempts = 3
    while True:
        await scrape(urls)
        if not values["failure"]:
            break
        if max_attempts > 0:
            logging.info(f"Retrying Failed Urls. Url Count: {len(values['failure'])}")
            urls = list(values["failure"])
            values["failure"] = []
            max_attempts -= 1
        else:
            logging.error(f"Failed Urls: {values['failure']}")
            break
    logging.info(f"Successful scrapes: {len(values['success'])}/{urlcount}")
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        logging.info(values["success"])
        futures = [executor.submit(trim, values["success"][url], url)
                   for url in values["success"]]
        for future in futures:
            try:
                future.result()
            except Exception as e:
                logging.error(f"Error while trimming: {e}")


if __name__ == "__main__":
    urls = []
    with open("urls.csv", "r") as file:
        csv_reader = csv.reader(file)
        header = next(csv_reader)
        for row in csv_reader:
            urls.append(row[0])
    asyncio.run(main(urls))