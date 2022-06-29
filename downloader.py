# downloader.py ~ The code on this file is in charge of looping through the UN library
# on a given range of years, under the search of "Tribute to the memory of h** excellency ambassador".
# It downloads all PDFs available for each year into a year-specific folder.
# Two databases are created. One that registers the URL that each PDF comes from in the UN library.
# The other serves as a log file, being a record of those URLs where the download failed for some reason.

import bs4, requests
import os
import pandas as pd

# Global variables of relevance
URL = 'https://digitallibrary.un.org/search?ln=en&p=%22Tribute%20to%20the%20memory%20of%20h**%20excellency%20ambassador%22&f=&rm=&ln=en&sf=&so=d&rg=50&c=Resource%20Type&c=UN%20Bodies&c=&of=hb&fti=1&fti=1&fct__3='
BASE_LINK = "https://digitallibrary.un.org"
PDF_DIR = os.getcwd() + '/PDFs'

# Databases
links_data = {'File': [],
              'URL': []}

log = {'URL': []}
df = pd.DataFrame(links_data)
log_df = pd.DataFrame(log)


def get_urls(site):
    """Finds URLs of each library entry on a year's main website."""

    _urls = []
    data = requests.get(site)
    html = bs4.BeautifulSoup(data.text, 'html.parser')
    my_divs = html.find_all("div", {"class": "result-title"})

    for div in my_divs:
        links = div.findAll('a')
        for a in links:
            _urls.append(BASE_LINK + a['href'])

    return _urls


def download_pdf(download_site, year):
    """Given a website including the PDF files, it downloads
    its English version."""

    dir = os.path.join(PDF_DIR, str(year))
    site = requests.get(download_site)
    html = bs4.BeautifulSoup(site.text, 'html.parser')

    metas = html.find_all("meta", {"name": "citation_pdf_url"})
    meta = next(filter(lambda x: x['content'].endswith('EN.pdf') or x['content'].endswith('v1.pdf'), metas), None)

    print('Downloading ', meta['content'])
    pdf_link = meta['content']
    filename = pdf_link[pdf_link.rfind('/'):]
    response = requests.get(pdf_link)
    pdf = open(dir + filename, 'wb')
    pdf.write(response.content)
    pdf.close()
    df.loc[len(df.index)] = [filename, download_site]


def get_all_pdfs(site, year):
    """Downloads all PDFs on a year's website."""

    urls = get_urls(site)
    for url in urls:
        print('At ', url)
        try:
            download_pdf(url, year)
        except TypeError:
            print('Failed to download. Omitting...')
            log_df.loc[len(df.index)] = [url]


def main(start, end):
    """Main function. Given a start year and an end year,
    it downloads all PDFs of all those years into year-specific
    folders."""

    for x in range(start, end + 1):
        os.mkdir(os.path.join(PDF_DIR, str(x)))
        print('At year ', x)
        site = URL + str(x)
        get_all_pdfs(site, x)

    df.to_csv('links_data.csv')
    log_df.to_csv('log.csv')


# main(1981, 2022)

