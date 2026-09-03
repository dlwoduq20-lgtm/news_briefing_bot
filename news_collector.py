import os
import sys
import urllib.parse
import feedparser
import requests
from bs4 import BeautifulSoup
from typing import List, Dict
import logging

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

class NewsCollector:
    """
    글로벌 거시경제(금리, 환율, 미국 증시), 빅테크(엔비디아, 애플 등),
    그리고 대상 자산(삼성전자, SK하이닉스, 비트코인)의 핵심 뉴스와 본문 내용을 종합 수집합니다.
    """
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    def fetch_rss_news(self, query: str, max_items: int = 5) -> List[Dict]:
        """
        Google News RSS를 통해 검색어 관련 뉴스를 수집합니다.
        """
        encoded_query = urllib.parse.quote(query)
        rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=ko&gl=KR&ceid=KR:ko"
        
        feed = feedparser.parse(rss_url)
        items = []
        
        for entry in feed.entries[:max_items]:
            title = entry.get("title", "").strip()
            link = entry.get("link", "").strip()
            published = entry.get("published", "")
            summary_html = entry.get("summary", "")
            
            # HTML 태그 제거 및 텍스트 정제
            soup = BeautifulSoup(summary_html, "html.parser")
            clean_summary = soup.get_text(separator=" ").strip()
            
            source = ""
            if " - " in title:
                parts = title.rsplit(" - ", 1)
                clean_title = parts[0].strip()
                source = parts[1].strip()
            else:
                clean_title = title
            
            items.append({
                "title": clean_title,
                "source": source,
                "link": link,
                "summary": clean_summary,
                "published": published
            })
            
        return items

    def collect_macro_and_market_context(self) -> List[Dict]:
        """
        주가에 직접적인 영향을 주는 글로벌 거시(금리, 환율, 미국 뉴욕증시, 필라델피아 반도체 지수, 엔비디아/빅테크 실적) 뉴스를 수집합니다.
        """
        queries = [
            "미국 뉴욕증시 반도체 엔비디아 마감",
            "미 연준 기준금리 환율 FOMC",
            "필라델피아 반도체 지수 빅테크 실적"
        ]
        macro_news = []
        seen = set()
        for q in queries:
            items = self.fetch_rss_news(q, max_items=3)
            for it in items:
                key = it["title"][:20]
                if key not in seen:
                    seen.add(key)
                    macro_news.append(it)
        logging.info(f"[글로벌 거시/빅테크] 뉴스 수집 완료: {len(macro_news)}건")
        return macro_news[:5]

    def collect_asset_news(self, asset_info: Dict, max_total: int = 5) -> List[Dict]:
        """
        특정 자산의 여러 검색 쿼리로부터 뉴스를 종합 수집하고 중복을 제거합니다.
        """
        asset_name = asset_info["name"]
        queries = asset_info.get("search_queries", [asset_name])
        
        all_news = []
        seen_titles = set()
        
        for q in queries:
            news_items = self.fetch_rss_news(q, max_items=4)
            for item in news_items:
                title_key = item["title"][:20].replace(" ", "")
                if title_key not in seen_titles:
                    seen_titles.add(title_key)
                    all_news.append(item)
                if len(all_news) >= max_total:
                    break
            if len(all_news) >= max_total:
                break
                
        logging.info(f"[{asset_name}] 뉴스 수집 완료: {len(all_news)}건")
        return all_news

    def collect_all_with_macro(self, target_assets: Dict) -> Dict:
        """
        전체 대상 자산 뉴스와 함께 글로벌 거시/빅테크 시황을 함께 수집합니다.
        """
        macro_data = self.collect_macro_and_market_context()
        asset_data = {}
        for key, info in target_assets.items():
            asset_data[key] = self.collect_asset_news(info)

        return {
            "macro": macro_data,
            "assets": asset_data
        }

if __name__ == "__main__":
    from config import TARGET_ASSETS
    collector = NewsCollector()
    data = collector.collect_all_with_macro(TARGET_ASSETS)
    print("\n--- 글로벌 거시 시황 ---")
    for it in data["macro"]:
        print(f"• [{it['source']}] {it['title']}")
