import urllib.request
import json

from urllib.parse import quote, unquote

import requests

from html.parser import HTMLParser

import re

DEBUG = True

wikipediaApiSearchUrl = "https://en.wikipedia.org/w/api.php?action=opensearch&redirects=resolve&namespace=0&format=json&search="
#use redirects=resolve to get actual pages that has been redirected
wikipediaApiQueryUrl = "https://en.wikipedia.org/w/api.php?action=query&format=json&titles="

wikipediaArticleLinksUrl = ".wikipedia.org/w/api.php?action=query&redirects&pllimit=500&format=json&prop=links&titles="

wikipediaApiUrl = ".wikipedia.org/w/api.php"

#Must create a valid language table

def search2(searchString, lang="en"):
    #Maybe implement later, open search performs better due to better abstract and not including useless titles
    #https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch=Java&utf8=&srprop=titlesnippet|size|wordcount|timestamp|snippet|redirecttitle|redirectsnippet|sectiontitle|sectionsnippet&srlimit=500&srinterwiki
    return 0


#read this later:https://www.mediawiki.org/wiki/API:Search_and_discovery
#Open search returns the start string only results to use for autocompletition
def search(searchString, lang="en"):

    #Replace some things that are tecnically invalid to search
    searchString = searchString.replace("#", " sharp ")


    #Get the wikipedia api query result in bytes
    try:
        #queryResult = urllib.request.urlopen(wikipediaApiSearchUrl + queryString).read()

        #Convert to json string and then to a python object
        #queryObj = json.loads(queryResult.decode("utf-8"))
        requestParams = {
            'action': 'opensearch',
            'redirects':'resolve',
            'namespace':'0',
            'format':'json',
            'search': searchString
        } 

        queryObj = requests.get("https://" + lang + wikipediaApiUrl, params = requestParams).json()

        resultTitles = queryObj[1]  #Get the titles
        resultDescriptions = queryObj[2] #Get the descriptions
        resultUrls = queryObj[3]    #Get the urls

        resultLength = len(resultTitles)

    except Exception as e:
        return None

    #Get the min length of the properties get (expected to all be the same length)
    if len(resultDescriptions) < resultLength:
        resultLength = len(resultDescriptions)

    if len(resultUrls) < resultLength:
        resultLength = len(resultUrls)

    resultObject = []

    for i in range(0, resultLength):
        #Remove undesired results that contents the following
        if " may refer to:" in resultDescriptions[i]:
            continue
            
        #Get the last path index
        lastPathIndex = resultUrls[i].rfind("/") + 1

        resultObject.append({
            'title': resultTitles[i].replace("_", " "),
            'description': resultDescriptions[i],
            'url': resultUrls[i],
            'urlTitle': resultUrls[i][lastPathIndex:] #Get the substring of the url that means its title.
        })

        #Must use urltitle to avoid bugs in case of some symbols

    return resultObject














def queryPageLinks(page, lang="en"):
    #Get the wikipedia api query result in bytes
    try:
        #queryResult = urllib.request.urlopen("https://" + lang + wikipediaArticleLinksUrl + page).read()
        return baseQuery({
            'titles': page,
            'redirects': True,
            'pllimit':500,
            'format': 'jsonfm',
            'prop':'links',
        }, lang)


    except Exception as e:
        if DEBUG:
            raise e
        else:
            return None


#for result in query({'generator': 'allpages', 'prop': 'links'}):
    # process result data

def baseQuery(request, lang):

    queryResults = []

    request['action'] = 'query'

    lastContinue = {'continue': ''}
    while True:
        # Clone original request
        req = request.copy()
        # Modify it with the values returned in the 'continue' section of the last result.
        req.update(lastContinue)

        #Create query string
        #queryString = "?"
        #for key, value in req.items():
            #value = str(value) #Convert to string in case the value is not
            #queryString += key + "=" + value + "&"

        # Call API
        #result = urllib.request.urlopen('http://' + lang + '.wikipedia.org/w/api.php' + queryString).read()
        result = requests.get('http://en.wikipedia.org/w/api.php', params=req).text
        return result;
        if 'error' in result:
            raise Error(result['error'])
        if 'warnings' in result:
            print(result['warnings'])
        if 'query' in result:
            #yield result['query']
            queryResults.append(result['query'])
        if 'continue' not in result:
            break
        lastContinue = result['continue']

    return queryResults


def query(queryTitle, lang='en'):
    #Get the wikipedia api query result in bytes
    try:
        #queryResult = urllib.request.urlopen(wikipediaApiQueryUrl + queryTitle).read()

        #Convert to json string and then to a python object
        #queryObj = json.loads(queryResult.decode("utf-8")) 
        #queryObj = requests.get(wikipediaApiQueryUrl + queryTitle).json()
        #?action=query&format=json&titles="
        reqParams = {
            'action': 'query',
            'format': 'json',
            'titles': queryTitle
        }

        queryObj = requests.get("https://" + lang + wikipediaApiUrl, params=reqParams).json()

        #Ensure there is a query, a pages and there is no -1 (no results) in the pages
        if not "query" in queryObj:
            raise Exception("Expected query object on wikipedia api response")        
            
        if not "pages" in queryObj["query"]:
            raise Exception("Expected page object on wikipedia api query object") 
            
        if "-1" in queryObj["query"]["pages"]:
            raise Exception("Not results were returned from wikipedia api query.(-1 code)") 

        #Return the first page in the results
        for page in queryObj["query"]["pages"]:
            pageObj = queryObj["query"]["pages"][page]
            return {
                'title': pageObj["title"],
                'pageid': pageObj["pageid"],
                'urlTitle': queryTitle
            }
        
        raise Exception("Not results were returned from wikipedia api query. (Empty pages object)") 

    except Exception as e:
        if DEBUG:
            raise e
        else:
            return None


#Test url: #http://nvgtt-utils.mybluemix.net/wikipedia-nonreverse-links?page=c%2b%2b
def getAbstractNonReverseLinks(page, lang="en"):

    reqParams = {
        'page': page,
        'lang': lang
    }

    result = requests.get("http://nvgtt-utils.mybluemix.net/wikipedia-nonreverse-links", params=reqParams).json()

    if 'error' in result:
        return []

    return result



def getPageAbstractLinks(page, lang="en"):

    #Ensure page is unquoted cause requests will quote it (gambiarra)
    page=unquote(page)

    #We got a issue (solved):

    #In case we send a query string with ++ by form:
        #The form converts the symbol to utf8 codes
        #on arrive, django convert it back to symbol format
        #we got to reconvert it to utf8 codes in order to post on wikipedia api (requests lib does that for us)

    #In case we send a query string with ++ by hyperlink
        #The browser ignores the ++ symbols
        #on arrive the query without ++ is gotten
        #we got nothing to do since the data were removed. We must supply the hyperlink already utf8 coded

        #detect reverse links
        #start storing link into the django db for this
        #on mouse over boxes, description about it will be show
        #remove reverse is a good approach, but no perfect

    try:

        #If no page specified, return error
        if not page:
            raise Exception("ERROR: No page specified.")

        #TestLink: https://en.wikipedia.org/w/api.php?action=parse&redirects&section=0&prop=text&format=jsonfm&page=C%2B%2B;

        #requestUrl = "https://" + lang + ".wikipedia.org/w/api.php?action=parse&redirects&section=0&prop=text&format=json;

        requestUrl = "https://" + lang + wikipediaApiUrl

        reqParams = {
            'action': 'parse',
            'page':page,
            'redirects': True,
            'section': 0,
            'prop': 'text',
            'format':'json'
        }

        reqvalue = requests.get(requestUrl, params=reqParams).text

        startIndex = reqvalue.find("<")

        #If no < were found, means error. Raise it
        if startIndex == -1:
            raise Exception(reqvalue)

        endIndex = reqvalue.rfind(">") + 1

        #Get pageId pattern:"pageid":5200013,
        pageIdMatches = re.findall('"pageid":([0-9]+)', reqvalue)
        
        #Get page id 
        pageId = pageIdMatches[0] if len(pageIdMatches) > 0 else -1

        #Get the html portion of the response
        htmlData = reqvalue[startIndex:endIndex]

        parser = ParseParagraphLinks() #Create parser
        parser.feed(htmlData) #feed the parse with the html content


        abstractLinks = []
        abstractLinksRaw = [] #Used for avoid repetition

        #Iterate thru the gotten links
        for link in parser.getLinks():
            if link.find('\"/wiki/') != 1: #get only wiki links
                continue
            
            endIndex = link.rfind('\"') - 1
            newLink = link[8:endIndex]

            if newLink in abstractLinksRaw: #If the link already exists in abstractLinks raw
                continue #Proceed next iteration

            abstractLinksRaw.append(newLink) #Otherwise, add it to the raw values

            #Add wikilink obj to the result array
            abstractLinks.append({
                'title': unquote(newLink).replace("_", " "),
                'href': newLink   
            })


            #Replace utf8 "encoded" chars
            #newLink = fixUtf8Chars(newLink)
                
            #abstractLinks[newLink] = {
                #'title': fixUtf8Chars(newLink),
                #'link': newLink        
            #}

            #if not newLink in abstractLinks: #If the link does not exits in the list
                #abstractLinks.append(newLink) #format it properly

        return {
            'article': unquote(page).replace("_", " "),
            'articleUrl': page,
            'pageId': pageId,
            'abstractLinks': abstractLinks
        }
        
    except Exception as e:
        return {
            'article': unquote(page).replace("_", " "),
            'pageId': -1,
            'abstractLinks': [],
            'error': str(e)      
        }




def getTrueWikiLink(page, lang="en"):
    return normalizeWikiLink(page, lang)


#Function to return the true link in case of any redirection is present on the page
#Example url: https://en.wikipedia.org/w/api.php?action=opensearch&redirects=resolve&limit=1&format=jsonfm&search=Tibia_(computer_game)
def normalizeWikiLink(page, lang='en'):

    reqParams = {
        'action': 'opensearch',
        'redirects': 'resolve',
        'limit': 1,
        'format': 'json',
        'search': page
    }

    resultObj = requests.get("https://" + lang + wikipediaApiUrl, params=reqParams).json()

    
    if 'error' in resultObj:
        print(resultObj['error'])
        return False

    if len(resultObj[3]) == 0:
        print('GetTrueLinks ERROR: No results.')
        return False

    #Get the result string
    resultAddr = resultObj[3][0]
    #Get the last path index
    lastPathIndex = resultAddr.rfind("/") + 1
    #Return the last path (true link)
    return resultAddr[lastPathIndex:]


def getUTF8Codes(targetString):
    targetString = targetString.replace("+", "%2B")
    return targetString

def fxUtf8Chars(targetString):
    formatedString = targetString

    #Dedicated formats to avoid bugs
    formatedString = formatedString.replace("%E2%80%93", "-")
    formatedString = formatedString.replace("%C3%A7", "ç")

    #Get expresion with starts with %, number from 0 to 7, and then an hex OR 
    #Get expresion starting with %c or %d, followed by an hex, a % and then 2 consecutive hex
    utf8Matches = re.findall("%[0-7][a-f0-9]|%[cd][a-f0-9]%[a-f0-9]{2}", formatedString, flags=re.IGNORECASE)

    for match in utf8Matches:
        #Remove all % symbols
        noPercent = match.replace("%", "")
        #Decode the byte string to the utf8 char
        utfChar = bytearray.fromhex(noPercent).decode('utf-8')
        #Replace the occurrence
        formatedString = formatedString.replace(match, utfChar)

    return formatedString





#Inheirited class to parse html elements
class ParseParagraphLinks(HTMLParser):

    def __init__(self):
        super().__init__() #Invoke base class constructor
        self.pTagCounter = 0 #Variable to sum up the number of nested paragraphs we have
        self.linksArray = [] #Array to store the links found
        #self.firstParagraph = ""
        #self.firstParagraphFlag = True #Flag to detect the first paragraph

    def getLinks(self):
        return self.linksArray

    #def getFirstParagraph(self):
        #return self.firstParagraph

    def handle_starttag(self, tag, attrs):
        if tag == 'p':
            self.pTagCounter += 1

        #If the found "a" tag is inside a "p" tag
        if tag == 'a' and self.pTagCounter > 0:
            #Iterate thru the attributes
            for attr in attrs:
                if attr[0] == 'href': #If the current is the href
                    self.linksArray.append(attr[1]) #append its content
                    break #Exit the iteration
        
    def handle_endtag(self, tag):
        if tag == 'p':
            self.pTagCounter -= 1
            self.firstParagraphFlag = False

    #def handle_data(self, data):
        #if self.pTagCounter == 1 and self.firstParagraphFlag:
            #self.firstParagraph += data
        #print("Encountered some data  :", data)
