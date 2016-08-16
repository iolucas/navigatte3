import urllib.request
import json

import requests

from navigatte.settings import DEBUG

from html.parser import HTMLParser

import re

wikipediaApiSearchUrl = "https://en.wikipedia.org/w/api.php?action=opensearch&redirects=resolve&namespace=0&format=json&search="
#use redirects=resolve to get actual pages that has been redirected
wikipediaApiQueryUrl = "https://en.wikipedia.org/w/api.php?action=query&format=json&titles="

wikipediaArticleLinksUrl = ".wikipedia.org/w/api.php?action=query&redirects&pllimit=500&format=json&prop=links&titles="

def search(queryString):
    #Get the wikipedia api query result in bytes
    try:
        queryResult = urllib.request.urlopen(wikipediaApiSearchUrl + queryString).read()

        #Convert to json string and then to a python object
        queryObj = json.loads(queryResult.decode("utf-8")) 

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
        #Remove undesired results
        if " may refer to:" in resultDescriptions[i]:
            continue

        resultObject.append({
            'title': resultTitles[i],
            'description': resultDescriptions[i],
            'url': resultUrls[i],
            'urlTitle': resultUrls[i][30:] #Get the substring of the url that means its title
        })

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


def query(queryTitle):
    #Get the wikipedia api query result in bytes
    try:
        queryResult = urllib.request.urlopen(wikipediaApiQueryUrl + queryTitle).read()

        #Convert to json string and then to a python object
        queryObj = json.loads(queryResult.decode("utf-8")) 

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




def getPageAbstractLinks(page, lang="en"):

    #If no page specified, return error
    if not page:
        raise Exception("ERROR: No page specified.")

    requestUrl = "https://" + lang + ".wikipedia.org/w/api.php?action=parse&redirects&section=0&prop=text&format=json&page=" + page

    reqvalue = requests.get(requestUrl).text

    startIndex = reqvalue.find("<")

    #If no < were found, means error. Raise it
    if startIndex == -1:
        raise Exception(reqvalue)

    endIndex = reqvalue.rfind(">") + 1

    #Get the html portion of the response
    htmlData = reqvalue[startIndex:endIndex]


    parser = ParseParagraphLinks() #Create parser
    parser.feed(htmlData) #feed the parse with the html content

    wikiLinks = []

    #Iterate thru the gotten links
    for link in parser.getLinks():
        if link.find('\"/wiki/') != 1: #get only wiki links
            continue
        
        endIndex = link.rfind('\"') - 1
        newLink = link[8:endIndex]

        #Replace utf8 "encoded" chars
        newLink = fixUtf8Chars(newLink)
            
        if not newLink in wikiLinks: #If the link does not exits in the list
            wikiLinks.append(newLink) #format it properly

    return wikiLinks



def fixUtf8Chars(targetString):
    formatedString = targetString

    #Dedicated formats to avoid bugs
    formatedString = formatedString.replace("%E2%80%93", "-")
    formatedString = formatedString.replace("%C3%A7", "ç")

    #Get expresion starting with %c or %d, followed by an hex, a % and then 2 consecutive hex
    utf8Matches = re.findall("%[cd][a-f0-9]%[a-f0-9]{2}", formatedString, flags=re.IGNORECASE)

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

    pTagCounter = 0 #Variable to sum up the number of nested paragraphs we have
    linksArray = [] #Array to store the links found

    def getLinks(self):
        return self.linksArray

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

    #def handle_data(self, data):
        #print("Encountered some data  :", data)