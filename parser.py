# parser.py ~ The code on this file is in charge of parsing each PDF file on the PDFs folder
# in search of phrases matching the string "to the memory of". Upon finding a match, it loads
# the phrase to the df.csv database along with the PDF document it comes from, the document's URL
# and the year it was published by the UN.

import os
import re
import pandas as pd
import fitz  # install using: pip install PyMuPDF


data = {'File': [],
        'URL': [],
        'Year': [],
        'Phrases': []}

# Databases.
df = pd.DataFrame(data)
url_data = pd.read_csv('links_data.csv')


def read_pdf(file):
    """Returns the text of a PDF file."""
    with fitz.open(file) as doc:
        text = ""
        for page in doc:
            text += page.get_text()

    return text


def find_in_memoriam(text, phrase_length=100):
    """Returns an in memoriam phrase -id est, a phrase
    that includes 'to the memory of'- in given text.
    Parameter phrase_length tells how much of the phrase will
    be returned"""

    positions = [m.start() for m in re.finditer('to the memory of', text)]
    phrases = []
    for pos in positions:
        phrases.append(text[pos - phrase_length:pos + phrase_length])

    return phrases


def load_data():
    """Main function. Parses through each PDF file on each year folder,
    reads the PDF and searches for in memoriam phrases. Upon finding any,
    it readily loads to the database its relevant information: file, year,
    url and phrase."""

    for folder in os.listdir('PDFs'):
        print('At year ', folder)
        for file in os.listdir(os.path.join('PDFs', folder)):
            url = url_data[url_data['File'] == '/' + file].values[0][2]
            txt = read_pdf(os.path.join(os.path.join('PDFs', folder), file))
            phrases = find_in_memoriam(txt)
            if len(phrases) == 0:
                continue
            print('At ', file)
            print('Found ', len(phrases), ' phrases')
            for phrase in phrases:
                df.loc[len(df.index)] = [file, url, folder, phrase]

    print(df)
    df.to_csv('df.csv')


# load_data()

