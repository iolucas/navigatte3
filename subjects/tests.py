from django.test import TestCase

# Create your tests here.

from .models import Subject

from django.contrib.auth.models import User

class SubjectsTests(TestCase):

    #Execute routines before testing (creating or getting resources, etc)
    def setUp(self):
        #Create users for testing
        self.testPassword = "TestPassword"

        self.testUser = "TestUser"
        self.testUser2 = "TestUser2"

        User.objects.create_user(username=self.testUser, password=self.testPassword)
        User.objects.create_user(username=self.testUser2, password=self.testPassword)

#Tests for subjects display view

    def test_subjects_display_invalid_user(self):
        response = self.client.get("/Invalid" + self.testUser + "/")
        self.assertEqual(response.status_code, 404, "Expected 404 code in a invalid user")

    def test_subjects_display_valid_not_logged_user(self):
        response = self.client.get("/" + self.testUser + "/")
        self.assertEqual(response.status_code, 200, "Expected 200 code in a valid user")
        self.assertEqual(response.context['userpage'], self.testUser, "Expected same user on login and context.")
        self.assertEqual(response.context['isOwner'], False, "Expected not to be the owner.")
        self.assertEqual(len(response.context['subject_list']), 0, "Expected empty subjects list.")
 
    def test_subjects_display_valid_ownership(self):
        self.assertEqual(self.client.login(username=self.testUser, password=self.testPassword),True,
            "Expected user to be able to loggin")
        
        response = self.client.get("/" + self.testUser + "/")
        self.assertEqual(response.context['isOwner'], True, "Expected to be the owner.")

        response = self.client.get("/" + self.testUser2 + "/")
        self.assertEqual(response.context['isOwner'], False, "Expected not to be the owner.")


#Tests for subjects add view

    def test_subjects_add(self):
        #Verify if the user subject is empty
        response = self.client.get("/" + self.testUser + "/")
        self.assertEqual(len(response.context['subject_list']), 0, "Expected empty subjects list.")

        #Login user
        self.client.login(username=self.testUser, password=self.testPassword)
        
        #Post add new subject
        response = self.client.post("/" + self.testUser + "/add/", {'subject_name': 'TestSubject'})
        
        response = self.client.get("/" + self.testUser + "/")
        self.assertEqual(len(response.context['subject_list']), 1, "Expected not empty subjects list.")

        #Check same name of the 1 subject
        self.assertEqual(response.context['subject_list'][0].name, 'TestSubject', "Expected same new subject name.")

        #Post add new subject in the screen of other user
        response = self.client.post("/" + self.testUser2 + "/add/", {'subject_name': 'TestSubject2'})
        
        response = self.client.get("/" + self.testUser2 + "/")
        self.assertEqual(len(response.context['subject_list']), 0, "Expected empty subjects list.")

        response = self.client.get("/" + self.testUser + "/")
        self.assertEqual(len(response.context['subject_list']), 2, "Expected not empty subjects list.")

        #Check same name of the 1 subject
        self.assertEqual(response.context['subject_list'][1].name, 'TestSubject2', "Expected same new subject name.")
        


    def test_subjects_display_not_empty(self):
        pass

    def test_subjects_add_not_logged(self):
        pass

    def test_subjects_add_logged(self):
        pass

    def test_subjects_remove(self):
        pass

    def test_subjects_add_logged_different_userpage(self):
        pass

    def test_subjects_details_display(self):
        pass

    def test_subjects_reference_add(self):
        pass

    def test_subjects_reference_remove(self):
        pass