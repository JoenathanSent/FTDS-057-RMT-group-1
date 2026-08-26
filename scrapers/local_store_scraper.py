import os, sys
import pandas as pd
import datetime as dt
from pathlib import Path

from local.hexacom import HexacomScraper
from local.klikgalaxy import KlikGalaxyScraper
from local.nano import NanoScraper

from local.product_group_mapper.cpu_classifier import classify_cpu_group, extract_cpu_type
from local.product_group_mapper.gpu_classifier import classify_gpu_group, extract_gpu_type
from local.product_group_mapper.ram_classifier import classify_ram_group

hexacom_cat_map = {
    'MOTHERBOARD': 'MOTHERBOARDS',
    'PROCESSOR': 'PROCESSORS',
    'MEMORY (RAM)': 'MEMORY',
    'VGA CARD': 'GRAPHICS CARDS',
    'POWER SUPPLY': 'POWER SUPPLIES',
    'CASING': 'CASES',
    'SSD': 'SOLID STATE DRIVES',
    'MONITOR': 'MONITORS',
    'CPU COOLER': 'CPU COOLERS'
}

gasol_cat_map = {
    'Mainboard': 'MOTHERBOARDS',
    'Processor': 'PROCESSORS',
    'Memory': 'MEMORY',
    'VGA Card': 'GRAPHICS CARDS',
    'POWER SUPPLY': 'POWER SUPPLIES',
    'Casing PC': 'CASES',
    'HardDisk - SSD': 'SOLID STATE DRIVES',
    'Monitor - Bracket': 'MONITORS',
    'Cooler - Modding Kit': 'CPU COOLERS'
}

nano_cat_map = {
    'for Intel Processor': 'MOTHERBOARDS',
    'for AMD Processor': 'MOTHERBOARDS',
    'Intel Processor': 'PROCESSORS',
    'AMD Processor': 'PROCESSORS',
    'Desktop Memory': 'MEMORY',
    'Laptop Memory': 'MEMORY',
    'Workstation Memory': 'MEMORY',
    'NVIDIA Professional Graphics': 'GRAPHICS CARDS',
    'NVIDIA GeForce Graphic Card': 'GRAPHICS CARDS',
    'AMD Radeon Graphic Card': 'GRAPHICS CARDS',
    'Fully Modular PSU': 'POWER SUPPLIES',
    'Semi Modular PSU': 'POWER SUPPLIES',
    'Non Modular PSU': 'POWER SUPPLIES',
    'Full Tower Case': 'CASES',
    'Mid Tower Case': 'CASES',
    'Mini Tower Case': 'CASES',
    'Small Form Factor Case': 'CASES',
    'NVME SSD': 'SOLID STATE DRIVES',
    'SATA SSD': 'SOLID STATE DRIVES',
    'Monitor - Bracket': 'MONITORS',
    'CPU Air Cooler': 'CPU COOLERS',
    'CPU AIO Water Cooler': 'CPU COOLERS',
}

group_mappers = {
    'PROCESSORS': classify_cpu_group,
    'GRAPHICS CARDS': classify_gpu_group,
    'MEMORY': classify_ram_group
}

type_extractors = {
    'PROCESSORS': extract_cpu_type,
    'GRAPHICS CARDS': extract_gpu_type,
}

def classify_group(row):
    cat = row['pangoly_category']
    if cat is None:
        return None
    fn = None if cat not in group_mappers else group_mappers[cat]
    if fn is not None:
        return fn(row['product_name'])
    return None

def extract_type(row):
    cat = row['pangoly_category']
    if cat is None:
        return None
    if cat == 'MEMORY':
        return row['pangoly_group']
    fn = type_extractors.get(cat)
    if fn is not None:
        return fn(row['product_name'])
    return None

def standardize(raw: pd.DataFrame, cat_mapper: dict) -> pd.DataFrame:
    df = raw.copy()
    df = df.dropna(subset=['price_idr'])
    df['pangoly_category'] = df['category'].map(cat_mapper)
    df['pangoly_group'] = df.apply(classify_group, axis=1)
    df['actual_type'] = df.apply(extract_type, axis=1)
    return df

def scrape_all(file_path = None):
    try:
        print("-- scraping hexacom ...")
        hex_scraper = HexacomScraper()
        hex_df = hex_scraper.scrape()
        hex_df = standardize(hex_df, hexacom_cat_map)

        print("-- scraping klikgalaxy ...")
        gasol_scraper = KlikGalaxyScraper()
        gasol_df = gasol_scraper.scrape()
        gasol_df = standardize(gasol_df, gasol_cat_map)

        print("-- scraping nanokomputer ...")
        nano_scraper = NanoScraper()
        nano_df = nano_scraper.scrape()
        nano_df = standardize(nano_df, nano_cat_map)

        df = pd.concat([hex_df, gasol_df, nano_df])

        if df is None:
            print("df is empty, nothing is saved")
            return

        if file_path is None:
            current_date = dt.datetime.now().strftime('%Y-%m-%d')
            folder_path = f'./local_price_data/created_date={current_date}'
            os.makedirs(folder_path, exist_ok=True)
            file_path = f'{folder_path}/local_price.csv'

        df.to_csv(file_path, index=False)
        print("\ndf is saved to ", file_path)


    except Exception as e:
        print('Error scraping:', e)
        raise e

if __name__ == "__main__":
    file_path = sys.argv[1]
    scrape_all(file_path)