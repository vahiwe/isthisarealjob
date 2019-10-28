from flask import Flask, render_template, url_for, request
import requests
from bs4 import BeautifulSoup
from textblob import TextBlob
import matplotlib.pyplot as plt
import urllib
import nltk
import spacy
# import en_core_web_sm
import pytesseract as pt
from nltk.corpus import stopwords
from PIL import Image
from gingerit.gingerit import GingerIt
import googlemaps

# nltk.download("stopwords") # downloading nltk stop words
# nltk.download("punkt")
# assigning variables
# nlp = en_core_web_sm.load()
stop_words = stopwords.words("english")
gmaps = googlemaps.Client(key='AIzaSyAlvT9QoXecXq_WFfd4_slajtCnMJBXB6Y')
pt.pytesseract.tesseract_cmd = '/app/.apt/usr/bin/tesseract'
WordList = []
correction = ""
auth = ""
neg = ""
# ldefine a folder to store and later serve the images
UPLOAD_FOLDER = '/static/uploads/'

# allow files of a specific type
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])



app = Flask(__name__)

@app.route('/',methods=['POST','GET'])
def home():
    global correction
    global auth
    global neg
    startload = True
    if request.method == 'POST':
        if 'submit' in request.form:
            searchTerm = str(request.form['message'])
            board = 29

            try:
                j = 0
                while j < 20:
                    if j == 0:
                        nextItem = False
                    else:
                        nextItem = True
                    commentsCurrent = search_item(searchTerm, nextItem, j,  board)
                    add_to_word_list(commentsCurrent)
                    j += 1
            except:
                titlee = "Search failed"
                common = "Try again"
                startload = False
                st = True
                conf = False
                if correction != "" and auth != "" and neg != "":
                    conf = True
                    st = False
                return render_template('home.html', starter = startload, conf=conf, starte=True, sta=True, st=st, searcht= titlee, poip=common)            

            polarity = 0
            positive = 0
            negative = 0
            neutral = 0


            previous = []

            for tweet in WordList:
                if tweet in previous:
                    continue
                previous.append(tweet)
                analysis = TextBlob(tweet)
                """evaluating polarity of comments"""
                polarity += analysis.sentiment.polarity

                if (analysis.sentiment.polarity == 0):
                    neutral += 1
                elif (analysis.sentiment.polarity < 0.00):
                    negative += 1
                elif (analysis.sentiment.polarity > 0.0):
                    positive += 1

            noOfSearchTerms = positive + negative + neutral

            positive = percentage(positive, noOfSearchTerms)
            negative = percentage(negative, noOfSearchTerms)
            neutral = percentage(neutral, noOfSearchTerms)
            neg = negative

            titl = "How people are reacting on " + searchTerm + " by analyzing " + str(noOfSearchTerms) + " comments from " + "on nairaland"

            if (negative> 30):
                comm = "There is a high percentage of negative comments about this Company online in regards to jobs"
            elif(negative>20):
                comm = "There are some negative comments about this Company in regards to jobs" 
            elif (negative<20):
                comm = "There is a low percentage of negative comments about this Company online in regards to jobs"

            startload = False
            st = True
            conf = False
            if correction != "" and auth != "" and neg != "":
                conf = True
                st = False
            return render_template('home.html', starter = startload, conf=conf, starte=True, sta=True, st=st, searcht= titl, poip=comm)
        elif 'verify' in request.form:
            addressTerm = str(request.form['address'])
            addr = verify_address(addressTerm)
            startload = True
            st = True
            conf = False
            if addr == "The Company address is valid":
                cont = "This address looks legit"
                auth = True
            else:
                cont = "This address might be bogus"
                auth = False
            if correction != "" and auth != "" and neg != "":
                conf = True
                st = False
            return render_template('home.html', starter = startload, conf=conf, starte=False, sta=True, st=st, searcht=addr, poip=cont)
        elif 'check' in request.form:
            inviteTerm = str(request.form['invite'])
            inv = check(inviteTerm)
            correction = inv
            if inv == 0:
                cont = "There are no errors in this invitation"
            else:
                cont = "You have errors in this invitation"
            startload = True
            st = True
            conf = False
            if correction != "" and auth != "" and neg != "":
                conf = True
                st = False
            return render_template('home.html', starter = startload, starte=True, sta=False, st=st, conf=conf, searcht=inv, poip=cont)
        elif 'reset' in request.form:
            conf = False
            if correction != "" and auth != "" and neg != "":
                conf = True
            return render_template('home.html', starter = startload, starte=True, conf=conf, sta=True, st=False, searcht= "",poip="")
        elif 'confidence' in request.form:
            report = confidence_interval()
            correction = ""
            auth = ""
            neg = ""
            return render_template('home.html', starter = startload, conf=False, starte=True, report=report, sta=True, st=False, searcht= "",poip="")
    return render_template('home.html', starter = startload, starte=True, sta=True, conf=False, st=False, searcht= "",poip="")

# route and function to handle the upload page
@app.route('/upload', methods=['GET', 'POST'])
def upload_page():
    if request.method == 'POST':
        # check if there is a file in the request
        if 'file' not in request.files:
            return render_template('upload.html', msg='No file selected')
        file = request.files['file']
        # if no file is selected
        if file.filename == '':
            return render_template('upload.html', msg='No file selected')

        if file and allowed_file(file.filename):

            # call the OCR function on it
            extracted_text = file_type(file)

            if extracted_text == '':
                replyy = 'Sorry Character could not be clearly recognized'
                return render_template('upload.html',
                                   msg=replyy)
            # extract the text and display it
            return render_template('upload.html',
                                   msg='Successfully processed',
                                   extracted_text=extracted_text)
    
    return render_template('upload.html')

def percentage(part, whole):
    """function to calculate percentage"""
    return round((100 * float(part)/float(whole)),2)


def word_count(string):
    """function to return count of comments"""
    counts = dict()
    words = string.split()

    for word in words:
        if word in counts:
            counts[word] += 1
        else:
            counts[word] = 1

    return len(counts)


def search_item(search_term, next=False, page=0,  board=0):
    """function to search and return comments"""
    if next == False:
        page = requests.get("https://www.nairaland.com/search?q=" + urllib.parse.quote_plus(str(search_term)) + "&board="+str(board))
    else:
        page = requests.get("https://www.nairaland.com/search/"
                            + str(search_term) + "/0/"+str(board)+"/0/1" + str(page))
    soup = BeautifulSoup(page.content, 'html.parser')

    comments = soup.findAll("div", {"class": "narrow"})

    return comments


def add_to_word_list(strings):
    """function to add all comments to Wordlist"""
    WordList
    k = 0
    while k < len(strings):
        if word_count(strings[k].text) > 1:
            WordList.append(strings[k].text)
        k += 1

# function to check the file extension
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# defining useful functions
def file_type(filename):# function for character optical recognition
    s = Image.open(filename)
    text = pt.image_to_string(s)
    return text


# check for grammer and spelling errors and return the number of corrections
def check(filename):
    f = word(filename, 'sentence')
    corrections = 0
    for s in f:
        g = GingerIt()
        h = g.parse(s)
        corrections += len(h['corrections'])
    return corrections

def word(filename, final_type): # function to tokenize text 
        tok_sent = nltk.sent_tokenize(filename)
        tok_word = []
        for s in tok_sent:
            tok_word.append(nltk.word_tokenize(s))
        final_text = []
        for w in tok_word:
            if w not in stop_words:
                final_text.append(w)
        if final_type == 'sentence':
            return tok_sent
        elif final_type == 'word':
            return final_text

def verify_address(address):    
    geocode_result = gmaps.geocode(address)
    # if geocode_result != '[]':
    #     return "Address verified"
    # else:
    #     return "Couldn't verify address"
    if geocode_result == []:
        return "This address is invalid"
    else:
        geocode_result= geocode_result[0]
        if 'plus_code' in geocode_result:
            return "The Company address is valid"
        else:
            return "This address is vague, This job invite is likely a scam"

def confidence_interval():
    global correction
    global auth
    global neg
    nega = float(neg)
    correc = float(correction)
    # correction = check(filename)
    # positive, negative, neutral = sentiment(searchTerm)
    # auth = verify_address(address)
    if auth:
        score_a = 5
    else:
        score_a = -5
        
    if nega < 20:
        score_n = 10
    elif nega >=20 and nega < 30:
        score_n = 5
    elif nega >= 30:
        score_n = 0
        
    if correc <= 5:
        score_c = 10
    elif correc > 5 and correc <= 10:
        score_c = 5
    elif correc > 10:
        score_c = 10
        
    confidence = ((score_a + score_n + score_c) / 30) * 10
    
    if confidence > 6:
        return "Based on logistics the job invite no be scam"
    if confidence >= 4 and confidence <= 6:
        return "The job invite shows elements of scam but not too sure"
    if confidence < 4:
        return "This is likely a scam"


if __name__ == '__main__':
    app.run(debug=True)
