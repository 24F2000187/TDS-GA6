import re
from playwright.sync_api import sync_playwright

SEEDS = ["55", "56", "57", "58", "59", "60", "61", "62", "63", "64"]  # Your 10 assigned seeds
EXPECTED_TOTAL = 2480465  # Precomputed target sum

def main():
    total = 0
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        for seed in SEEDS:
            url = f"https://sanand0.github.io/tdsdata/js_table/?seed={seed}"
            print(f"Scraping {url}...")
            page.goto(url, wait_until="networkidle")
            page.wait_for_selector("table")
            cells = page.locator("table td").all_inner_texts()
            for cell_text in cells:
                match = re.search(r"-?\d+(\.\d+)?", cell_text.strip())
                if match:
                    total += float(match.group())
        browser.close()

    int_total = int(round(total))
    print(f"TOTAL_SUM={int_total}")
    assert int_total == EXPECTED_TOTAL, f"Scraped sum ({int_total}) does not match expected ({EXPECTED_TOTAL})!"
    print("Scraping completed successfully.")

if __name__ == "__main__":
    main()
