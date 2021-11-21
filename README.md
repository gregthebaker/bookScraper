This is a python scraper for gathering data from books.toscrape.com about the science and poetry books.

It relies on the following python packages:
urllib
bs4 #BeautifulSoup
sqlite3
pandas
re

USAGE: 
python3 bookScraper.py

NOTES:
Ideally, this code should be modified to use prepared statements/stored procedures to make sure that malicious SQL statements are not inadvertently saved to the database. 

All monetary values shown are in British Pounds Sterling

You can test that the data is saved to the database using your favorite sql interpreter, I use sqllite3

To test from the commandline run:

sqlite3 libraryBooks.db "SELECT * from books;"


