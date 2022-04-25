from django.test import TestCase
from django.test import Client
from . import models
from django.contrib.auth.models import User
from django.db.utils import OperationalError



class SecurityTest(TestCase):
	def setUp(self):
		# Every test needs a client.
		self.client = Client()	
		# Create some users
		User.objects.create_user('user1', 'user1@example.com', 'p*2sfHQP==')
        	

	def test_classic_sql_injection(self):
		# ensure the user is logged out
		self.client.logout()
		# Issue a GET request.
		response = self.client.get('/tasktracker/')
		# Check that the response is 302 Found (Found after a redirect)
		self.assertEqual(response.status_code, 302)

		# response is an HttpResponseRedirect object
		self.assertEqual(response.url, "/accounts/login/")
		
		# try to use the rogue credentials
		response = self.client.post(response.url, {'username': "1' or '1' = '1" , 'password': "1' or '1' = '1"})  
		# Check that the response is 200 OK (no redirect to authenticated page)
		self.assertEqual(response.status_code, 200)
		# Checks the error message
		self.assertTrue(b"Your username and password didn't match" in response.content)


	def test_drop_table(self):
		# try to use the rogue data
		rogue_data = {
			'title': "'); DROP TABLE tasktracker_task; --" , 
			'due_date': "2022-05-01", 
			'status':'I'
		}
		
		self.client.login(username='user1', password='p*2sfHQP==')
		response = self.client.post("/tasktracker/add/", rogue_data) 
		self.assertEqual(len(models.Task.objects.all()), 1)

			
			
