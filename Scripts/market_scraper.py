"""
Market Scraper - TopCV Vietnam
v4.7 Week 1 Prototype

Simple, pragmatic scraper - no over-engineering!
"""
import sqlite3
import re
import json
from pathlib import Path
from datetime import datetime, date
from typing import Dict, List, Optional
import time

try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_OK = True
except ImportError:
    print("❌ Cài playwright trước: pip install playwright")
    print("   Sau đó: python -m playwright install chromium")
    PLAYWRIGHT_OK = False

# Optional: stealth mode (not critical for MVP)
try:
    from playwright_stealth import stealth_sync
    STEALTH_OK = True
except ImportError:
    STEALTH_OK = False
    print("⚠️  playwright-stealth not found (optional, continuing without it)")

DB_PATH = Path(__file__).parent.parent / '.ai_coach' / 'progress.db'


class TopCVScraper:
    """
    Scraper đơn giản cho TopCV
    Mục tiêu: job count + salary range cho mỗi skill
    """
    
    def __init__(self):
        self.base_url = "https://www.topcv.vn"
        
    def parse_salary(self, text: str) -> Optional[Dict]:
        """
        Parse VN salary formats:
        - "20 - 30 triệu"
        - "Upto 2000$"
        - "Thỏa thuận"
        
        Returns: {min: int, max: int, avg: int} in VND
        """
        if not text or "thỏa thuận" in text.lower():
            return None
            
        # Convert $ to VND (approximately)
        text = text.replace(',', '').replace('.', '')
        
        # Pattern: "20 - 30 triệu"
        match = re.search(r'(\d+)\s*-\s*(\d+)\s*(triệu|tr)', text, re.IGNORECASE)
        if match:
            min_val = int(match.group(1)) * 1_000_000
            max_val = int(match.group(2)) * 1_000_000
            return {
                'min': min_val,
                'max': max_val,
                'avg': (min_val + max_val) // 2
            }
        
        # Pattern: "Upto 2000$"
        match = re.search(r'(upto|up to)\s*(\d+)\s*\$', text, re.IGNORECASE)
        if match:
            max_usd = int(match.group(2))
            max_vnd = max_usd * 25000  # Rough conversion
            return {
                'min': max_vnd // 2,
                'max': max_vnd,
                'avg': max_vnd * 3 // 4
            }
        
        return None
    
    def scrape_skill(self, skill_name: str, max_pages: int = 1) -> Dict:
        """
        Scrape TopCV for a skill
        
        Args:
            skill_name: "Python", "Java", etc.
            max_pages: Chỉ scrape 1 page (20 jobs) để test
            
        Returns:
            {
                'job_count': int,
                'salaries': [int, int, ...],
                'salary_avg': int,
                'companies': [str, ...]
            }
        """
        print(f"🔍 Scraping TopCV for: {skill_name}")
        
        with sync_playwright() as p:
            # Launch browser (headless for speed)
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            # Stealth mode (optional - bypass bot detection)
            if STEALTH_OK:
                stealth_sync(page)
            
            # Search URL
            search_url = f"{self.base_url}/viec-lam/{skill_name.lower()}"
            
            try:
                page.goto(search_url, timeout=30000)
                time.sleep(2)  # Let page load
                
                # Extract job count
                job_count_elem = page.query_selector('.total-job, .job-count, h2')
                job_count = 0
                if job_count_elem:
                    text = job_count_elem.inner_text()
                    match = re.search(r'(\d+[\.,]?\d*)', text.replace('.', '').replace(',', ''))
                    if match:
                        job_count = int(match.group(1))
                
                # Extract salaries from job cards
                salaries = []
                salary_elements = page.query_selector_all('.salary, .job-salary, [class*="salary"]')
                
                for elem in salary_elements[:20]:  # First 20 jobs
                    salary_text = elem.inner_text()
                    parsed = self.parse_salary(salary_text)
                    if parsed:
                        salaries.append(parsed['avg'])
                
                # Calculate average
                salary_avg = sum(salaries) // len(salaries) if salaries else 0
                
                print(f"  ✅ Found: {job_count} jobs, avg salary: {salary_avg/1e6:.1f}M VND")
                
                browser.close()
                
                return {
                    'job_count': job_count,
                    'salaries': salaries,
                    'salary_avg': salary_avg,
                    'salary_min': min(salaries) if salaries else 0,
                    'salary_max': max(salaries) if salaries else 0,
                    'source': 'topcv'
                }
                
            except Exception as e:
                print(f"  ❌ Error: {e}")
                browser.close()
                return None
    
    def save_to_db(self, skill_name: str, data: Dict):
        """Save scraped data to database"""
        if not data:
            return
            
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        today = date.today().isoformat()
        
        cursor.execute("""
            INSERT OR REPLACE INTO market_data (
                skill_name, date, job_count,
                salary_min, salary_max, salary_avg,
                source, raw_data
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            skill_name,
            today,
            data['job_count'],
            data.get('salary_min', 0),
            data.get('salary_max', 0),
            data['salary_avg'],
            data['source'],
            json.dumps(data)
        ))
        
        conn.commit()
        conn.close()
        
        print(f"  💾 Saved to database")


def test_scraper():
    """Test với 5 skills hot"""
    scraper = TopCVScraper()
    
    test_skills = ['Python', 'Java', 'JavaScript', 'React', 'Node.js']
    
    print("🧪 Testing TopCV Scraper\n")
    
    for skill in test_skills:
        data = scraper.scrape_skill(skill)
        if data:
            scraper.save_to_db(skill, data)
        time.sleep(3)  # Be nice to server
        print()
    
    print("✅ Test complete!")


if __name__ == "__main__":
    test_scraper()
