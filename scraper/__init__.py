from bs4 import BeautifulSoup
import requests
import pandas as pd

'''
File ini berisi function untuk melakukan scraping pada beberapa toko komputer online.
Data yang diambil berasal dari search product.
'''


def scrape_hexacom(keyword: str) -> pd.DataFrame:
    '''
    Fungsi ini mengambil data dari hexacom
    
    Arguments:
      keyword (str) - product yang dicari
    
    Output:
      df (pd.Dataframe) - dataframe yang memiliki data product_name, url, price_idr
    
    Example:
      df = scrape_hexacom('rtx 5060')
    '''

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        }

        base_url = 'https://www.hexacom.id/search.php?keyword='
        url = f'{base_url}{keyword}'

        resp = requests.get(url, headers=headers, timeout=30)

        soup = BeautifulSoup(resp.text, 'lxml')

        listing = soup.find_all("div", {"class": "product-meta product-detail-container"})

        data = {"product_name": [], "url": [], "price_idr": []}
        for container in listing:
            name_container = container.find("h2", {"class": "name"})
            name = name_container.get_text()
            data["product_name"].append(name)

            url = name_container.find("a").get("href")
            data["url"].append(url)

            price = container.find("span", {"class": "price-list"}).get("data-price")
            data["price_idr"].append(price)

        return pd.DataFrame(data)

    except Exception as e:
        print(f"Error scraping hexacom: {e}")
        return None


def scrape_klikgalaxy(keyword: str) -> pd.DataFrame:
    '''
    Fungsi ini mengambil data dari klikgalaxy
    
    Arguments:
        keyword (str) - product yang dicari
    
    Output:
        df (pd.Dataframe) - dataframe yang memiliki data product_name, url, price_idr
    
    Example:
        df = scrape_klikgalaxy('rtx 5060')
    '''
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        }

        base_url = 'https://www.klikgalaxy.com/search.php?keyword='
        url = f'{base_url}{keyword}'

        resp = requests.get(url, headers=headers, timeout=30)

        soup = BeautifulSoup(resp.text, 'lxml')

        table = soup.find("table", {"id": "products-row"})

        data = {"product_name": [], "url": [], "price_idr": []}
        for title_container in table.find_all("h2", {"class": "product-title"}):
            name = title_container.get_text().strip()
            url = title_container.find("a").get("href")

            price_parent = title_container.find_parent("tr").find_next_sibling()
            price_span = price_parent.find("span", {"class": "product-price"})
            price = price_span.find("span").get("data-price")

            data["product_name"].append(name)
            data["url"].append(url)
            data["price_idr"].append(price)

        return pd.DataFrame(data)

    except Exception as e:
        print(f"Error scraping klikgalaxy: {e} ")
        return None


def scrape_nano(keyword: str) -> pd.DataFrame:
    '''
    Fungsi ini mengambil data dari nanokomputer
    
    Arguments:
        keyword (str) - product yang dicari
    
    Output:
        df (pd.Dataframe) - dataframe yang memiliki data product_name, url, price_idr
    
    Example:
        df = scrape_nano('rtx 5060')
    '''
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        }

        base_url = 'https://nanokomputer.com/search?q='
        url = f'{base_url}{keyword}'

        resp = requests.get(url, headers=headers, timeout=30)

        soup = BeautifulSoup(resp.text, 'lxml')

        listing = soup.find_all("li", {"class": "product-grid__item"})

        data = {"product_name": [], "url": [], "price_idr": []}
        for item in listing:
            name = item.find("p").get_text()
            url = "https://nanokomputer.com" + item.find("a").get("href")
            price_str = item.find("span", {"class": "price"}).get_text().replace("Rp", "").replace(".", "").strip()

            price = None
            try:
                price = int(price_str)
            except Exception as e:
                print(f"Failed converting price {price_str} to int: {e}")

            data["product_name"].append(name)
            data["url"].append(url)
            data["price_idr"].append(price)

        return pd.DataFrame(data)

    except Exception as e:
        print(f"Error scraping nanokomputer: {e}")
        return None