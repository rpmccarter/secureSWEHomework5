from django.test import TestCase
from django.test import Client
from django.contrib.auth.models import User
from .models import Task
class SecurityTest(TestCase):

	def setUp(self):
		username = "user1"
		password = "123456"
		email= "user1@nd.edu"
		User.objects.create_user(username, email, password)
		self.client = Client()

	def test1(self):
		response = self.client.get("/tasktracker/")
		# redirect is good
		self.assertEqual(response.status_code, 302)
		self.assertEqual(response.url, '/accounts/login/')
		# 
		my_input = {"username":"1' or '1' = '1",
		"password":"1' or '1' = '1"}
		response = self.client.post(
			response.url,
			my_input)
		error_message = b"Your username and password didn't match"
		self.assertTrue(error_message in response.content)


	def test2(self):
		self.client.login(username="user1",password="123456")
		my_input = {
			"title": "'); DROP TABLE tasktracker_task; --",
			"due_date":"2022-05-01",
			"status":"I"
		}
		response = self.client.post("/tasktracker/add", my_input)
		all_tasks = Task.objects.all()
		self.assertEqual(len(all_tasks), 1)
			
			

