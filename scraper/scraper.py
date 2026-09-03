from playwright.sync_api import sync_playwright , Locator , Route
import time
from seleniumbase import sb_cdp
from pathlib import Path
from constants import CAPTCHA_DOMAINS , MAX_RETRIES , RESOURCES
import random
from parser import parse_jobs
from storage import init_db, save_checkpoint



def block_resources(route : Route ) -> None :
    url = route.request.url
    if any(domain in url for domain in CAPTCHA_DOMAINS):
        route.continue_()
        return

    if route.request.resource_type in RESOURCES:
         route.abort()
    else:
         route.continue_()



def should_stop_scraping(next_button : Locator , cards : Locator , page_number : int ) -> bool :

    if next_button.count() == 0:
        print("No next button found. Stopping.")
        return True

    if cards.count() == 0:
        print(f"No jobs found on page {page_number}. Stopping.")
        return True
    
    return False





def scraper (searchword) :
    all_data = []
    init_db()

    sb = sb_cdp.Chrome()
    end_point = sb.get_endpoint_url()

    start = time.perf_counter()
    try :
        with sync_playwright() as p :

            # starting .
            browser = p.chromium.connect_over_cdp(end_point)
            context = browser.contexts[0]
            page = context.pages[0]

            page.route("**/*" , block_resources)
            cards = page.locator("div.mb-6.w-full.rounded.border.border-gray-400.bg-white")

            page_number = 1

            while True :
        
                print(f"Scraping page {page_number}...")
                success = False

                for attempt in range(1, MAX_RETRIES+1):
                    try :
                        page.goto(
                            f"https://wellfound.com/role/{searchword}?page={page_number}",
                            wait_until="domcontentloaded")
                        
                        if page.locator("iframe[src*='captcha']").count() > 0:
                            sb.solve_captcha()
                        page.wait_for_selector("div.mb-6.w-full.rounded.border.border-gray-400.bg-white")
                        success = True
                        break

                    except Exception as e:
                        print(f"⚠️ Attempt {attempt}/{MAX_RETRIES} failed on page {page_number}: {e}")
                        time.sleep(3)  
                if not success:
                    print(f"❌ Failed to load page {page_number}")
                    break

                try : 
                    data = parse_jobs(cards)
                    print(f"Page {page_number}: {len(data)} jobs extracted")
                    all_data.extend(data)

                except Exception as e:
                    print(f"⚠️ Failed to extract data on page {page_number}: {e}")
                    data = []


                if page_number % 5 == 0:
                    save_checkpoint(all_data,page_number)
                    all_data = []


                next_button = page.locator('a[aria-label="Next page"]')

                if should_stop_scraping(next_button , cards , page_number ) :
                    break 

                time.sleep(random.uniform(1, 3))
                page_number += 1
    finally:
        if all_data :
            save_checkpoint(all_data,page_number)
        sb.driver.quit()
        end = time.perf_counter()
        print(f"Time taken: {end - start:.2f} seconds")


