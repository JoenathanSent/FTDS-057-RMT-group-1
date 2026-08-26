from bs4 import BeautifulSoup

import requests, os, time
import pandas as pd
import datetime as dt

class KlikGalaxyScraper:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        }
        self.base_url = 'https://www.klikgalaxy.com'
        self.categories = {}
        self.df = pd.DataFrame()

    def scrape(self):
        self.scrape_categories()

        dfs = []
        for cat_name, data in self.categories.items():
            print('[scrape] category:', cat_name)
            for href in data['pages']:
                print('[scrape] scraping', href, '...')
                df = self.scrape_page(href)
                df['category'] = cat_name
                dfs.append(df)

        self.df = pd.concat(dfs)
        self.df['time'] = dt.datetime.now()
        self.df['source'] = 'klikgalaxy'

        return self.df

    def scrape_categories(self):
        resp = requests.get(self.base_url, headers=self.headers)
        soup = BeautifulSoup(resp.text, 'lxml')

        cat_list = soup.find_all('li', {'class': 'dir'})
        for cat in cat_list:
            link = cat.find('a')
            href = link.get('href')
            cat_name = link.get_text()
            page_links = self.get_page_links(href)
            page_links.append(f'{href}?o=a')
            self.categories[cat_name] = {'href': href, 'pages': page_links}

    def get_page_links(self, href):
        url = href if href.startswith('http') else f'{self.base_url}{href}'
        try:
            time.sleep(2)

            resp = requests.get(url, headers=self.headers)
            soup = BeautifulSoup(resp.text, 'lxml')

            pagination = soup.find('div', {'class': 'pagination'})
            if pagination is None:
                return []
            
            links = pagination.find_all('a')

            link_pages = set([])
            for link in links:
                href = link.get('href')
                link_pages.add(href)
            
            return list(link_pages)
        except Exception as e:
            print(f'Error getting page links for url {url}', e)
            return []

    def scrape_page(self, href):
        url = href if href.startswith('http') else f'{self.base_url}{href}'
        print(f'[scrape_page] scraping page {url} ...')
        try:
            resp = requests.get(url, headers=self.headers, timeout=30)
            
            soup = BeautifulSoup(resp.text, 'lxml')

            table = soup.find("table", {"id": "products-row"})
            tds = table.find_all("td", {"class": "hotitems"})

            data = {"product_name": [], "url": [], "price_idr": []}
            for td in tds:
                title = td.find('h2', {'class': 'product-title-column'})
                if title is None:
                    continue
                link = title.find('a', {'class': 'product-title-column'})
                name = link.get_text().strip()
                product_url = link.get("href")

                price_span = td.find("span", {"class": "product-price"})
                price_str = price_span.get_text()
                price = None
                try:
                    price = int(price_str.replace('Rp', '').replace('.', '').strip())
                except Exception as e:
                    print(f'[scrape page] error converting price: {e}')

                data["product_name"].append(name)
                data["url"].append(product_url)
                data["price_idr"].append(price)

            return pd.DataFrame(data)
        except Exception as e:
            print(f'[scrape_page] Error scraping {url}')
            raise e

    def save_to_csv(self, file_path = None):
        if self.df is None:
            print("df is empty, nothing is saved")
            return

        if file_path is None:
            folder_date = dt.datetime.now().strftime('%Y%m%d')
            folder_path = f'./data/{folder_date}'
            os.makedirs(folder_path, exist_ok=True)
            file_path = f'{folder_path}/klikgalaxy.csv'
        self.df.to_csv(file_path, index=False)
        print("\ndf is saved to ", file_path)


def run():
    scraper = KlikGalaxyScraper()
    scraper.scrape()
    scraper.save_to_csv()


if __name__ == '__main__':
    run()