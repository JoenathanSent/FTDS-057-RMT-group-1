from bs4 import BeautifulSoup

import requests, os, time
import pandas as pd
import datetime as dt

class NanoScraper:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        }
        self.base_url = 'https://nanokomputer.com'
        self.categories = {}
        self.df = pd.DataFrame()

    def scrape(self):
        self.scrape_categories()

        dfs = []
        for cat_name, data in self.categories.items():
            print('[scrape] category:', cat_name)

            i = 1
            while True:
                href = data['href'] + f'?page={i}'
                print('[scrape] href:', href)
                df = self.scrape_page(href)
                if df is None:
                    break
                i += 1
                df['category'] = cat_name
                dfs.append(df)
                time.sleep(2)

        self.df = pd.concat(dfs)
        self.df['time'] = dt.datetime.now()
        self.df['source'] = 'nanokomputer'

        return self.df
    
    def scrape_categories(self):
        resp = requests.get(self.base_url, headers=self.headers)
        soup = BeautifulSoup(resp.text, 'lxml')

        span_pc_comp = soup.find('span', {'class': 'menu-list__link-title'}, string='PC Component')
        parent_link = span_pc_comp.parent
        cat_menu = parent_link.find_next_sibling()

        cat_list = cat_menu.find_all('ul', {'class': 'simple-submenu__list simple-submenu__list--level-3 list-unstyled'})
        for cat in cat_list:
            links = cat.find_all('a')
            for link in links:
                href = link.get('href')
                cat_name = link.get_text().strip()
                self.categories[cat_name] = {'href': href, 'pages': []}

    def get_page_links(self, href):
        return []
    
    def scrape_page(self, href):
        url = href if href.startswith('http') else f'{self.base_url}{href}'
        try:
            resp = requests.get(url, headers=self.headers)
                        
            soup = BeautifulSoup(resp.text, 'lxml')
            contents = soup.find_all('product-card', {'class': 'product-card'})
            if contents is None or len(contents) == 0:
                print('[scrape page] no content found')
                return None

            data = {"product_name": [], "url": [], "price_idr": []}
            for content in contents:
                product_url = content.find('a').get('href')
                product_name = content.find('p').get_text()
                price_str = content.find('span', {'class': 'price'}).get_text()
                price = None
                try:
                    price = int(price_str.replace('Rp', '').replace('.', '').strip())
                except Exception as e:
                    print(f'[scrape page] Error casting price {price_str}')

                data['product_name'].append(product_name)
                data['url'].append(f'{self.base_url}{product_url}')
                data['price_idr'].append(price)

            return pd.DataFrame(data)
        except Exception as e:
            print(f'[scrape page] Error scraping {url}: {e}')

    def save_to_csv(self, file_path = None):
        if self.df is None:
            print("df is empty, nothing is saved")
            return

        if file_path is None:
            folder_date = dt.datetime.now().strftime('%Y%m%d')
            folder_path = f'./data/{folder_date}'
            os.makedirs(folder_path, exist_ok=True)
            file_path = f'{folder_path}/nano.csv'
        self.df.to_csv(file_path, index=False)
        print("\ndf is saved to ", file_path)


def run():
    scraper = NanoScraper()
    scraper.scrape()
    scraper.save_to_csv()

if __name__ == '__main__':
    run()