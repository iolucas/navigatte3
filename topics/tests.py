from django.test import TestCase

from django.contrib.auth.models import User

from .views import getOrCreateArticleByUrl, getOrCreateWikiUrl
from .models import WikiUrl, WikiArticle

from . import wikipedia_api2 as wikiapi

# Create your tests here.

class TestWikipediaApi(TestCase):

    def test_getPageAbstractLinksSuccess(self):
        print("Testing getPageAbstractLinks Success...")
        pageData = wikiapi.getPageAbstractLinks("C++", "en")

        #Check expected return object
        self.assertIsNotNone(pageData['title'])
        self.assertIsNotNone(pageData['pageId'])
        self.assertEqual(pageData['lang'], "en")
        self.assertIsNotNone(pageData['abstractLinks'])

        if 'error' in pageData:
            self.assertTrue(False, "The success pageData must not return an ERROR key.")

    def test_getPageAbstractLinksInvalidUrl(self):
        print("Testing getPageAbstractLinks InvalidUrl...")

        invalidUrl = 'sfasnfais'

        pageData = wikiapi.getPageAbstractLinks(invalidUrl, "en")

        #Check expected return object
        self.assertEqual(pageData['page'], invalidUrl, "The 'page' key in a invalid page data must be the same as the passed url.")

        if not 'error' in pageData:
            self.assertTrue(False, "The invalid url pageData must return an ERROR key.")

    def test_getPageAbstractLinksInvalidLanguage(self):
        print("Testing getPageAbstractLinks InvalidLanguage...")

        validUrl = 'C++'

        pageData = wikiapi.getPageAbstractLinks(validUrl, "sgsdgsdgs")

        #Check expected return object
        self.assertEqual(pageData['page'], validUrl, "The 'page' key in a invalid language data must be the same as the passed url.")

        if not 'error' in pageData:
            self.assertTrue(False, "The invalid url pageData must return an ERROR key.")
    

class TopicsFunctionsTest(TestCase):
    
    #This is called everytime a test starts
    def setUp(self):
        pass

    def test_getOrCreateWikiUrl(self):
        #create test user
        print("Creating test user...")
        testUserName = "TestUser"
        testUserPassword = "TestPassword"
        testUser = User.objects.create_user(username=testUserName, password=testUserPassword)

        print("Testing getOrCreateWikiUrl on create...")

        testWikiUrl, created = getOrCreateWikiUrl("testUrl", "pt", testUser)

        self.assertTrue(created, "The created flag must be set if the object has been created.")
        self.assertEqual(testWikiUrl.urlPath, "testUrl")
        self.assertEqual(testWikiUrl.language, "pt")
        self.assertEqual(testWikiUrl.createdBy, testUser)

        print("Testing getOrCreateWikiUrl on get...")

        testWikiUrl, created = getOrCreateWikiUrl("testUrl", "pt", testUser)

        self.assertFalse(created, "The created flag must NOT be set if the object has been get.")
        self.assertEqual(testWikiUrl.urlPath, "testUrl")
        self.assertEqual(testWikiUrl.language, "pt")
        self.assertEqual(testWikiUrl.createdBy, testUser)
        
    def test_getOrCreateArticleByUrl(self):
        #create test user
        print("Creating test user...")
        testUserName = "TestUser"
        testUserPassword = "TestPassword"
        testUser = User.objects.create_user(username=testUserName, password=testUserPassword)

        #Test Number 1
        print("Testing getOrCreateArticleByUrl on create and title and url are equal...")
        articleInstance, created = getOrCreateArticleByUrl("MQTT", "en", testUser)

        #for link in articleInstance.abstractUrls.all():
            #print(link.urlPath.encode('utf-8'))

        self.assertTrue(created)
        self.assertIsInstance(articleInstance, WikiArticle)
        self.assertEqual(articleInstance.title, "MQTT", "On this case, the article title and the the url are the same.")    
        self.assertEqual(articleInstance.language, "en") 

        #Test Number 2
        print("Testing getOrCreateArticleByUrl on get and title and url are different...")
        articleInstance, created = getOrCreateArticleByUrl("mqtt", "en", testUser)

        #for link in articleInstance.abstractUrls.all():
            #print(link.urlPath.encode('utf-8'))

        self.assertFalse(created)
        self.assertIsInstance(articleInstance, WikiArticle)
        self.assertNotEqual(articleInstance.title, "mqtt", "On this case, the article title and the the url are NOT the same.")    
        self.assertEqual(articleInstance.language, "en")          

        #Test Number 3
        print("Testing getOrCreateArticleByUrl with slashed (/) url and title different...")
        articleInstance, created = getOrCreateArticleByUrl("TCP/IP", "en", testUser)

        self.assertTrue(created)
        self.assertIsInstance(articleInstance, WikiArticle)
        self.assertNotEqual(articleInstance.title, "TCP/IP", "On this case, the article title and the the url are NOT the same.")    
        self.assertEqual(articleInstance.language, "en")

        #Test Number 4
        print("Testing getOrCreateArticleByUrl with invalid url...")
        articleInstance, created = getOrCreateArticleByUrl("asiuaisunas", "en", testUser)

        self.assertFalse(created)
        self.assertIsNone(articleInstance)

        #Test Number 5
        print("Testing getOrCreateArticleByUrl with invalid language...")
        articleInstance, created = getOrCreateArticleByUrl("C++", "asfaf", testUser)

        self.assertFalse(created)
        self.assertIsNone(articleInstance)
   
