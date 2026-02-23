from __future__ import annotations

from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from src.core.throttle import Throttle


@dataclass
class PageResult:
    url: str
    html: str


class FetchClient:
    def __init__(self, timeout: int = 20) -> None:
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "ScholarshipScraper/1.0 (compliance-first; contact: local-run)",
            }
        )
        self.throttle = Throttle()

    def fetch_static(self, url: str) -> PageResult:
        self.throttle.wait()
        response = self.session.get(url, timeout=self.timeout)
        response.raise_for_status()
        return PageResult(url=url, html=response.text)

    def fetch_dynamic(self, url: str, wait_seconds: float = 4.0) -> PageResult:
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        self.throttle.wait()
        driver = webdriver.Chrome(options=options)
        try:
            driver.get(url)
            driver.implicitly_wait(wait_seconds)
            html = driver.page_source
            return PageResult(url=url, html=html)
        finally:
            driver.quit()

    @staticmethod
    def to_soup(page: PageResult) -> BeautifulSoup:
        return BeautifulSoup(page.html, "html.parser")
