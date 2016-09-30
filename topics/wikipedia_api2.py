import sys #Module to access system stuff
import requests #Module to perform http requests
import re #Module to handle regular expressions
from html.parser import HTMLParser #Module to handle html tags
from urllib.parse import quote, unquote #Module to encode/decode urls strings


wikipediaApiUrl = ".wikipedia.org/w/api.php"

#On nodejs implementation this function was necessary
def encodeContinueUnicodeChar(text):
    pass
    #return text.replace(/\|0\|(.+)\|0\|/gi, function(match, character) {
        #return "|0|" + encodeURIComponent(character) + "|0|";
    #});


def getPageBackLinks(page, lang):
    #Test Url
    #https://en.wikipedia.org/w/api.php?action=query&list=backlinks&bltitle=Main%20Page&bllimit=5&blfilterredir=redirects
    #?action=query & format=json & list=backlinks & bllimit=250 & blnamespace=0 & blredirect & bltitle=" + page;

    #If no page or lang specified, return error
    if not page or not lang:
        raise Exception("No page or lang specified")

    requestUrl = "https://" + lang + wikipediaApiUrl

    #Params to return only the abstract of the wikipedia article (section 0)
    reqParams = {
        'action': 'query',
        'format': 'json',
        'list': 'backlinks',
        'bllimit': 250,
        'blnamespace': 0,
        'blredirect': True,
        'bltitle': page
    }

    backLinks = []  #Buffer to store links
    maxIterationCount = 100 #Max number of continues batches allowed

    #Keep doing this until break is called
    while True:

        #Perform request and convert result to json
        recObj = requests.get(requestUrl, params=reqParams).json()

        #Iterate thru the pages
        for pageObj in recObj['query']['backlinks']:
            
            backLinks.append(pageObj['title'])

            #If there is redirect links, push them to the backLinks too
            if 'redirlinks' in pageObj:
                for redirlink in pageObj['redirlinks']:
                    backLinks.append(redirlink['title'])

        #Subtract max iteration count
        maxIterationCount -= 1

        #If there is a continue object, proceed to the next batch,
        if 'continue' in recObj and maxIterationCount > 0:
            reqParams['blcontinue'] = recObj['continue']['blcontinue']
            #printUtf8(reqParams['blcontinue'])
        else: #If not, exit iteration
            break


    #Filter backlinks
    filteredBacklinks = []

    for bl in backLinks:
        #If the link already exists, proceed next iteration
        if bl in filteredBacklinks:
            continue

        #If the link is a desambiguation page
        if "(disambiguation)" in bl:
            continue

        #If the link is a list of something
        if "List of" in bl:
            continue

        #If the link is a index of something
        if "Index of" in bl:
            continue

        #If the link is a glossary of something
        if "Glossary of" in bl:
            continue

        filteredBacklinks.append(bl)

    return filteredBacklinks



def getPageAbstractLinks(page, lang="en"):

    try:

        #If no page specified, return error
        if not page:
            raise Exception("ERROR: No page specified.")

        #TestLink: https://en.wikipedia.org/w/api.php?action=parse&redirects&section=0&prop=text&format=jsonfm&page=C%2B%2B;

        requestUrl = "https://" + lang + wikipediaApiUrl

        #Params to return only the abstract of the wikipedia article (section 0)
        reqParams = {
            'action': 'parse',
            'page': page,
            'redirects': True,
            'section': 0,
            'prop': 'text',
            'format':'json'
        }

        #Handle answer as text because as json it crashs due to some convertion bug some times
        reqvalue = requests.get(requestUrl, params=reqParams).text

        #Get start of abstract html tag
        startIndex = reqvalue.find("<")

        #If no < were found, means error. Raise it
        if startIndex == -1:
            raise Exception(reqvalue)

        endIndex = reqvalue.rfind(">") + 1

        #Get page title pattern:"title":"C++",
        pageTitleMatches = re.findall('"title":"([^,]+)",', reqvalue)

        if len(pageTitleMatches) == 0:
            raise Exception("ERROR: No page title received.")

        #Get pageId pattern:"pageid":5200013, (Get any character except the comma)
        pageIdMatches = re.findall('"pageid":([^,]+),', reqvalue)

        if len(pageIdMatches) == 0:
            raise Exception("ERROR: No page id received.")        
        

        pageTitle = pageTitleMatches[0] #Get page title
        pageId = pageIdMatches[0] #Get page id 

        #Get the html portion of the response
        htmlData = reqvalue[startIndex:endIndex]

        parser = ParseParagraphLinks() #Create parser
        parser.feed(htmlData) #feed the parse with the html content

        abstractLinks = []

        #Iterate thru the gotten links
        for link in parser.getLinks():
            if link.find('\"/wiki/') != 1: #get only wiki links
                continue
            
            endIndex = link.rfind('\"') - 1
            newLink = link[8:endIndex]


            #Append abstract wiki links
            abstractLinks.append(unquote(newLink)) 


        return {
            'title': pageTitle,
            'pageId': pageId,
            'lang': lang,
            'abstractLinks': abstractLinks,
            #'abstract': parser.getTextContent()
        }
        
    except Exception as e:
        return {
            'page': page,
            'error': str(e)      
        }


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


#Inheirited class to parse html elements
class ParseParagraphLinks(HTMLParser):

    def __init__(self):
        super().__init__() #Invoke base class constructor
        self.pTagCounter = 0 #Variable to sum up the number of nested paragraphs we have
        self.linksArray = [] #Array to store the links found
        self.textContent = ""
        #self.firstParagraph = ""
        #self.firstParagraphFlag = True #Flag to detect the first paragraph

    def getLinks(self):
        return self.linksArray

    def getTextContent(self):
        return self.textContent

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

    def handle_data(self, data):
        self.textContent += data
        #if self.pTagCounter == 1 and self.firstParagraphFlag:
            #self.firstParagraph += data
        #print("Encountered some data  :", data)


def printUtf8(str):
    return print(str.encode('utf-8'))


#Testing

#If we execute this module alone with test arg, test its functions
if __name__ == "__main__" and sys.argv[1] == "test":
    print("Testing wikipedia api2...\n")
    
    #queryResult = getPageAbstractLinks("c++")
    #print(str(queryResult))
    
    #print("")

    #queryResult = search("c++")
    #printUtf8(str(queryResult))

    queryResult = getPageBackLinks("tibia (computer game)", "en")
    printUtf8(str(queryResult))
    print(len(queryResult))