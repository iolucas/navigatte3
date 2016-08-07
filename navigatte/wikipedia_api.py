import urllib.request
import json

from navigatte.settings import DEBUG

wikipediaApiSearchUrl = "https://en.wikipedia.org/w/api.php?action=opensearch&redirects=resolve&namespace=0&format=json&search="
#use redirects=resolve to get actual pages that has been redirected
wikipediaApiQueryUrl = "https://en.wikipedia.org/w/api.php?action=query&format=json&titles="


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
