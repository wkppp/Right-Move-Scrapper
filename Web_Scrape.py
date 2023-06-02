import sys

from playwright.sync_api import sync_playwright
import pandas as pd
import os, argparse
from pathlib import Path

target_url = "https://www.rightmove.co.uk/property-to-rent.html"

parse = argparse.ArgumentParser(prog="Small Web Scrape Task", description="A web scrapper")
parse.add_argument("-s", "--search", metavar="", help="Enter the area that you want to search", required=True)
parse.add_argument("-r", "--radius", metavar="",
                   help="Only accepts float values (1.0, 2.0, etc). Note that you must divide by one in selecting "
                        "fractional radius like 1/4 to 0.25", default=0.25)
parse.add_argument("-mnb", "--min_bedroom", metavar="", help="Enter the minimum bedroom spec", default=3)
parse.add_argument("-mxb", "--max_bedroom", metavar="", help="Enter the maximum bedroom spec", default=3)
parse.add_argument("-i", "--includeProperties", action="store_true", help="Include Agreed Properties?")
parse.add_argument("-f", "--file_name", metavar="", help="Enter the csv filename", default="Sample.csv", required=True)
parse.add_argument("-a", "--append", action="store_true", help="Are you just going to append on the file?")

args = parse.parse_args()

if len(sys.argv) <= 1:
    parse.print_help()
    sys.exit()

path = os.path.join(Path.cwd(), args.file_name)



def run(playwright):
    print("[+] Launch Browser")
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    print("[+] Entering the url")
    page.goto(target_url)
    print("[+] Filling in req field")
    page.get_by_placeholder("e.g. 'York', 'NW3', 'NW3 5TY' or 'Waterloo station'").click()
    page.get_by_placeholder("e.g. 'York', 'NW3', 'NW3 5TY' or 'Waterloo station'").fill(args.search)
    page.get_by_role("button", name="Start Search").click()
    page.get_by_role("combobox", name="Search radius").select_option(str(args.radius))
    page.get_by_role("combobox", name="No. of bedrooms", exact=True).select_option(str(args.min_bedroom))
    page.get_by_role("combobox", name="Maximum No. of bedrooms").select_option(str(args.max_bedroom))
    if args.includeProperties:
        page.locator("#secondarycriteria span").click()
    page.get_by_role("button", name="Find properties").click()
    print("[+] Getting PostCode")
    pc = page.locator("[name=locationIdentifier]").get_attribute("value")
    print(f"[+] PostCode: {pc.split('^')[1]}")
    save_to_csv(pc)


def save_to_csv(pc):
    print("[+] Save to csv")
    if args.append:
        df = pd.read_csv(path)
        data = {
            "Search": args.search,
            "PostCode": pc.split("^")[1]
        }
        df = df._append(data, ignore_index=True)
        df.to_csv(path, index=False)
    else:
        data = ({
            "Search": [args.search],
            "PostCode": [pc.split("^")[1]]
        })
        df = pd.DataFrame(data)
        df.to_csv(path, index=False)


with sync_playwright() as playwright:
    run(playwright)
