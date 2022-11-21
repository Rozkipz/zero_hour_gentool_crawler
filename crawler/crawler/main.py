import datetime
import logging
import sys
import time

import models
import requests

import db_interface

from bs4 import BeautifulSoup

GET_FAILURE_COUNT = 3


def get_page(url: str, timeout: int) -> str:
    failure_count = 0
    while True:
        try:
            start = time.time()
            page_req = requests.get(url, allow_redirects=True, timeout=timeout)
            end = time.time()
            print("Took {} seconds to get page from GT".format(end - start))

            if page_req.ok:
                return page_req.text
            else:
                page_req.raise_for_status()

        except Exception as e:  # For now catch all exceptions, but in the future we can handle specific return codes.
            if failure_count >= GET_FAILURE_COUNT:
                logging.exception('Failed to get page {}'.format(url))
                # If we fail to get the page `GET_FAILURE_COUNT` times, then give up and raise the http failure response.
                raise e

            failure_count += 1
            time.sleep(5)  # Maybe we are rate limited?


class GentoolCrawler:
    def __init__(self, url, timeout):
        self.url = url
        self.zh_url = url + '/zh'
        self.ccg_url = url + '/ccg'

        self.timeout = timeout

    def get_yesterday_player_data(self):
        now = datetime.datetime.now()
        yesterday = now - datetime.timedelta(days=1)

        yesterday_month_fmt = yesterday.strftime("%Y_%m_%B")
        yesterday_fmt = yesterday.strftime("%d_%A")
        page_url = f"{self.zh_url}/{yesterday_month_fmt}/{yesterday_fmt}/"
        yesterdays_player_data = get_page(page_url, timeout=self.timeout)

        parsed_data = BeautifulSoup(yesterdays_player_data, 'html.parser')
        for row in parsed_data.find_all('tr')[3:-1]:  # Remove the headers and parent dir link, and an empty row at the bottom.
            name_and_id = row.a["href"][:-1]  # Remove the trailing `/`
            name, playerid = name_and_id.rsplit('_', 1)  # Split on the last `_`

            p = models.player.Player(playerid, name)
            # print(p.as_dict())
            db_interface.upsert_player(p)


if __name__ == "__main__":
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] [%(filename)s:%(lineno)s - %(funcName)s] %(message)s")
    level = logging.NOTSET

    logging.basicConfig(level=logging.NOTSET)
    logger = logging.getLogger("crawler")
    stdout_log = logging.StreamHandler(stream=sys.stdout)
    stdout_log.setLevel(level)
    stdout_log.setFormatter(formatter)
    logger.addHandler(stdout_log)

    gentool_zh_url = 'https://gentool.net/data'
    req_timeout = 5  # Seconds
    crawler = GentoolCrawler(gentool_zh_url, req_timeout)
    crawler.get_yesterday_player_data()
