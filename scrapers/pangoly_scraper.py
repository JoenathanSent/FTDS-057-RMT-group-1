import sys
import datetime as dt

from historical.pangoly import scrape, save_to_csv

if __name__ == '__main__':
    file_path = sys.argv[1]

    df = scrape()
    save_to_csv(df, file_path)