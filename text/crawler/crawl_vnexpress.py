"""Crawl headlines and lead paragraphs (sapo) from VnExpress category pages.

Builds the Vietnamese news-topic dataset used in text/notebook.ipynb.
Only the title, the short lead and the article URL are stored (no article
bodies), for non-commercial coursework use.

Usage:
    pip install requests beautifulsoup4 pandas
    python text/crawler/crawl_vnexpress.py --pages 12 --out text/data/vnexpress_news.csv
"""
import argparse
import time
from datetime import datetime, timezone

import pandas as pd
import requests
from bs4 import BeautifulSoup

CATEGORIES = {
    "thoi-su": "Thời sự",
    "the-gioi": "Thế giới",
    "kinh-doanh": "Kinh doanh",
    "khoa-hoc-cong-nghe": "Khoa học - Công nghệ",
    "giai-tri": "Giải trí",
    "the-thao": "Thể thao",
    "phap-luat": "Pháp luật",
    "giao-duc": "Giáo dục",
    "suc-khoe": "Sức khỏe",
    "du-lich": "Du lịch",
}
HEADERS = {"User-Agent": "Mozilla/5.0 (academic course project; HCMUT CO5177)"}


def page_url(slug, page):
    return f"https://vnexpress.net/{slug}" if page == 1 else f"https://vnexpress.net/{slug}-p{page}"


def parse_page(html):
    soup = BeautifulSoup(html, "html.parser")
    rows = []
    for item in soup.select("article.item-news"):
        link = item.select_one(".title-news a")
        if link is None or not link.get("href"):
            continue
        desc = item.select_one(".description a") or item.select_one(".description")
        location = None
        description = None
        if desc is not None:
            stamp = desc.select_one(".location-stamp")
            if stamp is not None:
                location = stamp.get_text(strip=True)
                stamp.extract()
            description = desc.get_text(" ", strip=True) or None
        rows.append({
            "title": link.get("title") or link.get_text(strip=True),
            "description": description,
            "location": location,
            "url": link["href"].split("#")[0],
        })
    return rows


def crawl(pages, delay):
    records = []
    for slug, name in CATEGORIES.items():
        for page in range(1, pages + 1):
            url = page_url(slug, page)
            try:
                resp = requests.get(url, headers=HEADERS, timeout=20)
                resp.raise_for_status()
            except requests.RequestException as exc:
                print(f"  ! {url}: {exc}")
                continue
            rows = parse_page(resp.text)
            for r in rows:
                r.update(category_slug=slug, category=name, page=page)
            records.extend(rows)
            print(f"{slug:<20} p{page:<3} +{len(rows):>3}  total={len(records)}")
            time.sleep(delay)
    df = pd.DataFrame(records)
    df["crawled_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return df


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pages", type=int, default=12)
    parser.add_argument("--delay", type=float, default=1.0, help="seconds between requests")
    parser.add_argument("--out", default="text/data/vnexpress_news.csv")
    args = parser.parse_args()

    df = crawl(args.pages, args.delay)
    # Raw crawl is kept as-is (duplicates included); cleaning happens in the notebook.
    df.to_csv(args.out, index=False)
    print(f"Saved {len(df)} rows -> {args.out}")
