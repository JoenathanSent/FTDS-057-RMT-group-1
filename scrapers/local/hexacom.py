from bs4 import BeautifulSoup

import requests, os, time
import pandas as pd
import datetime as dt

class HexacomScraper:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        }
        self.base_url = 'https://www.hexacom.id'
        self.categories = {}
        self.df = pd.DataFrame()
    
    def scrape(self):
        self.scrape_categories()

        dfs = []
        for cat_name, data in self.categories.items():
            print('[scrape] category:', cat_name)
            print(data)
            for href in data['pages']:
                print('[scrape] scraping', href, '...')
                df = self.scrape_page(href)
                df['category'] = cat_name
                dfs.append(df)

        self.df = pd.concat(dfs)
        self.df['time'] = dt.datetime.now()
        self.df['source'] = 'hexacom'

        return self.df

    def scrape_categories(self):
        resp = requests.get(self.base_url, headers=self.headers)
        soup = BeautifulSoup(resp.text, 'lxml')

        container = soup.find('div', {'id': 'categories'})
        links = container.find_all('a')
        for link in links:
            href = link.get('href')
            if not href.startswith('http') and len(href.lstrip('/').split('/')) == 1:
                page_links = self.get_page_links(href)
                cat_name = link.find('span', {'class': 'menu-title'}).get_text()
                self.categories[cat_name] = { 'href': href, 'pages': page_links }

    def get_page_links(self, href):
        url = href if href.startswith('http') else f'{self.base_url}{href}'
        time.sleep(2)

        resp = requests.get(url, headers=self.headers)
        soup = BeautifulSoup(resp.text, 'lxml')

        container = soup.find('ul', {'class': 'pagination'})
        links = container.find_all('a', {'class': 'link-pages'})

        link_pages = set([])
        for link in links:
            href = link.get('href')
            link_pages.add(href)

        return list(link_pages)
    
    def scrape_page(self, href):
        url = f'{self.base_url}{href}'

        try:
            resp = requests.get(url, headers=self.headers)
            
            soup = BeautifulSoup(resp.text, 'lxml')
        
            listing = soup.find_all("div", {"class": "product-meta product-detail-container"})
        
            data = {"product_name": [], "url": [], "price_idr": []}
            for container in listing:
                name_container = container.find("h2", {"class": "name"})
                name = name_container.get_text()
                data["product_name"].append(name)
        
                product_url = name_container.find("a").get("href")
                data["url"].append(product_url)
        
                price_container = container.find("span", {"class": "price-list"})
                price = None if price_container is None else price_container.get("data-price")
                data["price_idr"].append(price)
        
            return pd.DataFrame(data)
        except Exception as e:
            print('Error scraping', url)
            raise e

    def save_to_csv(self, file_path = None):
        if self.df is None:
            print("df is empty, nothing is saved")
            return

        if file_path is None:
            folder_date = dt.datetime.now().strftime('%Y%m%d')
            folder_path = f'./data/{folder_date}'
            os.makedirs(folder_path, exist_ok=True)
            file_path = f'{folder_path}/hexacom.csv'
        self.df.to_csv(file_path, index=False)
        print("\ndf is saved to ", file_path)



def run():
    scraper = HexacomScraper()
    scraper.scrape()
    scraper.save_to_csv()

if __name__ == '__main__':
    run()