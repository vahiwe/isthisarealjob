# ML-TEAM3
System that predicts if a job invite received is real or a scam

## Requirements
* Libraries needed
    * Beautiful Soup [BeautifulSoup](https://pypi.org/project/beautifulsoup4/)
    * Matplotlib [Matplotlib](https://matplotlib.org/users/installing.html)
    * Textblob [Textblob](https://textblob.readthedocs.io/en/dev/)
* nlp_ner
   This program takes-in data in picture or text format, determines what it is, extract the text and get the amount of errors 
   in the document, also outputs the name of the company and location of the address found in the picture or text.
 
   Dependencies are:

   * nltk(stopwords, punkt tokenizer) for the sub-dependencies: python -m nltk.downloader punkt, python -m nltk.downloader stopwords
   * gingerit
   * pillow
   * spacy   sub-dependency: python -m spacy download en
   * pytesseract (python wrapper)
   * tesseract-ocr.exe gotten from https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-setup-v5.0.0-alpha.20191010.exe

   type pytesseract.pytesseract.tesseract_cmd = Installed location for tesseract-ocr in the python idle
 
   each of the main dependencies can be downloaded from cmd by pip install dependency


