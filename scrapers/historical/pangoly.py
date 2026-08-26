import random, os
import pandas as pd
import datetime as dt

from playwright.sync_api import sync_playwright

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}

def time_series_to_df(json_data, category, product):
    time_series = {'date': []}
    for key, val in json_data.items():
        if len(time_series['date']) == 0:
            time_series['date'] = [price[0] for price in val]
        time_series[key] = [price[1] for price in val]

    df = pd.DataFrame(time_series)
    df['date'] = pd.to_datetime(df['date'], unit='ms')
    df['category'] = category
    df['product'] = product

    return df

def scrape():
    url = 'https://pangoly.com/en/price-trends'
    cats = {}
    dfs = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(user_agent=headers['User-Agent'])

        page.goto(url)

        categories = page.locator('div.trends-category-section')
        num_of_cats = categories.count()
        print(f'Found {num_of_cats} categories')
        for i in range(num_of_cats):
            title = categories.nth(i).locator('h2.subpage-title').first.inner_text().strip()
            cats[title] = {}

            links = categories.nth(i).locator('a.trends-category-link')
            num_of_links = links.count()
            for j in range(num_of_links):
                link_url = links.nth(j).get_attribute('href')
                product_name = links.nth(j).inner_text()
                product_name = product_name.split('\n\n\n')[0].strip()
                cats[title][product_name] = link_url

        page.close()

        for cat, data in cats.items():
            print(f'\n==== {cat} ===')
            for product, product_url in data.items():
                print(f'product: {product}')
                print(f'url: {product_url}')

                ref = product_url.replace('https://pangoly.com/en/price-trends', '/data')
                print(f'time series data ref: {ref}')

                product_page = browser.new_page(user_agent=headers['User-Agent'])
                try:
                    try:
                        with product_page.expect_response(lambda r: ref in r.url, timeout=15000) as resp_info:
                            product_page.goto(product_url)
                            delay = random.randint(2000, 5000)
                            product_page.wait_for_timeout(delay)
                    except Exception as e:
                        print(f'  skipped: no matching response ({e})')
                        continue

                    resp = resp_info.value
                    if not resp.ok:
                        print(f'  skipped: HTTP {resp.status} for {resp.url}')
                        continue

                    body = resp.text()
                    if not body.strip():
                        print(f'  skipped: empty response body for {resp.url}')
                        continue

                    try:
                        json_data = resp.json()
                    except Exception as e:
                        print(f'  skipped: could not parse JSON ({e})')
                        continue

                    df = time_series_to_df(json_data, cat, product)
                    dfs.append(df)
                finally:
                    product_page.close()

        browser.close()

    if not dfs:
        print('\nno data scraped')
        return None

    df = pd.concat(dfs)
    return df

def save_to_csv(df, file_path):
    if df is not None:
        if file_path is None:
            folder_date = dt.datetime.now().strftime('%Y%m%d')
            folder_path = f'./data/{folder_date}'
            os.makedirs(folder_path, exist_ok=True)
            file_path = f'{folder_path}/pangoly.csv'
        df.to_csv(file_path, index=False)
        print("\ndf is saved to ", file_path)
    else:
        print("df is empty, nothing is saved")

def run():
    df = scrape()
    save_to_csv(df)


if __name__ == '__main__':
    run()