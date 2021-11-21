# import web grabbing client and
# HTML parser
from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup
import re
from urllib.parse import  urljoin, urlparse
import sqlite3
from sqlite3 import Error
import pandas as pd


def create_connection(db_file):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    return conn

def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)

def create_project(conn, project):
    """
    Create a new project into the projects table
    :param conn:
    :param project:
    :return: project id
    """
    sql = ''' INSERT INTO projects(name,begin_date,end_date)
              VALUES(?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, project)
    conn.commit()
    return cur.lastrowid

def create_book(conn, book):
    """
    Create a new task
    :param conn:
    :param book:
    :return:
    """

    sql = ''' INSERT INTO books(title,description,upc,product_type,price_at,price_bt,tax,availability,num_avail,num_reviews)
              VALUES(?,?,?,?,?,?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, book)
    conn.commit()
    return cur.lastrowid

def main():
    database = r"libraryBooks.db"

    sql_create_projects_table = """ CREATE TABLE IF NOT EXISTS projects (
                                        id integer PRIMARY KEY,
                                        name text NOT NULL,
                                        begin_date text,
                                        end_date text
                                    ); """

    sql_create_tasks_table = """CREATE TABLE IF NOT EXISTS books (
                                    id integer PRIMARY KEY,
                                    title text NOT NULL,
                                    description text,
                                    upc text NOT NULL,
                                    product_type text NOT NULL,
                                    price_at real NOT NULL,
                                    price_bt real NOT NULL,
                                    tax real NOT NULL,
                                    availability text NOT NULL,
                                    num_avail integer NOT NULL,
                                    num_reviews integer NOT NULL
                                );"""

    # create a database connection
    conn = create_connection(database)

    # create tables
    if conn is not None:
        # create projects table
        create_table(conn, sql_create_projects_table)

        # create tasks table
        create_table(conn, sql_create_tasks_table)
    else:
        print("Error! cannot create the database connection.")
    
    with conn:
        project = ('bookData', '2021-11-19', '2021-11-26');
        project_id = create_project(conn, project)

        # variable to store website link as string
        baseUrl = 'http://books.toscrape.com'
        indexUrl = baseUrl+'/index.html'
        # grab website and store in variable uclient
        uClient = uReq(indexUrl)
        page_html = uClient.read()
        uClient.close()
        
        # call BeautifulSoup for parsing
        page_soup = soup(page_html, "html.parser")
        
        # find the Science and Poetry links
        #page_links = page_soup.findAll('a', href=True)
        scienceUrl = urljoin(baseUrl,page_soup.find('a', {'href': re.compile(r'\/science_')}).get('href'))
        poetryUrl = urljoin(baseUrl,page_soup.find('a', {'href': re.compile(r'\/poetry_')}).get('href'))
        
        #grab science URL for parsing
        uSci = uReq(scienceUrl)
        sci_html = uSci.read()
        uSci.close()
        #grab science URL for parsing
        uPoe = uReq(poetryUrl)
        poe_html = uPoe.read()
        uPoe.close()
        
        sci_soup = soup(sci_html, "html.parser")
        poe_soup = soup(poe_html, "html.parser")


        #find portion of html that contains relative links to each book
        scibooks = sci_soup.findAll("article", {"class": "product_pod"})
        poebooks = poe_soup.findAll("article", {"class": "product_pod"})
        
        #iterate over the relative links to form links to each book page and append the urls to the list 'libraryLinks'
        libraryLinks = []
        for scibook in scibooks:
            index = urljoin(baseUrl,scibook.find('a', href=True).get('href'))
            url = urlparse(index).scheme+'://'+urlparse(index).netloc+'/catalogue'+urlparse(index).path
            libraryLinks.append(url)
        for poebook in poebooks:
            index = urljoin(baseUrl,poebook.find('a', href=True).get('href'))
            url = urlparse(index).scheme+'://'+urlparse(index).netloc+'/catalogue'+urlparse(index).path
            libraryLinks.append(url)
        #open each link in 'libraryLinks' for parsing and scraping
        for bookLink in libraryLinks:
            uBook = uReq(bookLink)
            book_html = uBook.read()
            uBook.close()
            book_soup = soup(book_html, "html.parser")
            #use pandas to find the product info table and extract the data, if the table were very large, it would be better to enumerate the values rather than hardcode their location in the table.
            book_info = pd.read_html(book_html)[0]
            upc = book_info.loc[0,1]
            product_type = book_info.loc[1,1]
            price_bt = float(re.findall("\d+\.\d+",book_info.loc[2,1])[0])
            price_at = float(re.findall("\d+\.\d+",book_info.loc[3,1])[0])
            tax = float(re.findall("\d+\.\d+",book_info.loc[4,1])[0])
            availability = book_info.loc[5,1]
            num_avail = int(re.findall(r'\d+', book_info.loc[5,1])[0])
            num_reviews = int(re.findall(r'\d+', book_info.loc[6,1])[0])
            #find the title and description of each book
            title = book_soup.find("div", {"class": "col-sm-6 product_main"}).h1.contents[0]
            description = book_soup.find("meta", {"name": "description"}).get('content')
            #save the data to the SQL database file
            book_data = (title, description, upc, product_type, price_at, price_bt, tax, availability, num_avail, num_reviews)
            create_book(conn, book_data)


if __name__ == '__main__':
    main()


