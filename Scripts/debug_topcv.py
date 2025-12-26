"""
Debug TopCV page structure
"""
from playwright.sync_api import sync_playwright
import time

def debug_topcv():
    """Inspect TopCV page để tìm đúng selectors"""
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Show browser
        page = browser.new_page()
        
        # Go to TopCV Python jobs
        page.goto("https://www.topcv.vn/viec-lam/python", timeout=30000)
        time.sleep(5)  # Wait for JS
        
        # Take screenshot
        page.screenshot(path="topcv_debug.png")
        print("✅ Screenshot saved: topcv_debug.png")
        
        # Get page HTML
        html = page.content()
        with open("topcv_debug.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("✅ HTML saved: topcv_debug.html")
        
        # Try to find job elements
        print("\n🔍 Looking for job count...")
        
        # Try various selectors
        selectors = [
            'h2', 'h1', '.total-job', '.job-count',
            '[class*="total"]', '[class*="count"]',
            'span', 'strong'
        ]
        
        for sel in selectors:
            elems = page.query_selector_all(sel)
            for elem in elems[:5]:  # First 5
                text = elem.inner_text().strip()
                if any(word in text.lower() for word in ['việc', 'job', 'tìm', 'công']):
                    print(f"  {sel}: {text}")
        
        input("\nPress Enter to close browser...")
        browser.close()

if __name__ == "__main__":
    debug_topcv()
