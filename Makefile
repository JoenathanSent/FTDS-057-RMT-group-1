scrape-local:
	python3 scrapers/local_store_scraper.py data/local_price_test.csv

scrape-pangoly:
	python3 scrapers/pangoly_scraper.py data/pangoly_test.csv