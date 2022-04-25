from django.test import TestCase
from django.test import Client
from django.contrib.auth.models import User
from .models import Task

class SecurityTest(TestCase):

	def setUp(self):
		username1 = "user1"
		password1 = "123456"
		email1= "user1@nd.edu"
		User.objects.create_user(username1, email1, password1)
		self.user1client = Client()

		username2 = "user2"
		password2 = "123456"
		email2 = "user2@nd.edu"
		User.objects.create_user(username2, email2, password2)
		self.user2client = Client()

	def test1(self):
		response = self.user1client.get("/tasktracker/")
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
		self.user1client.login(username="user1",password="123456")
		my_input = {
			"title": "'); DROP TABLE tasktracker_task; --",
			"due_date":"2022-05-01",
			"status":"I"
		}
		response = self.user1client.post("/tasktracker/add/", my_input)
		all_tasks = Task.objects.all()
		self.assertEqual(len(all_tasks), 1)
			
	def testHttpMethods(self):
		self.user1client.login(username="user1",password="123456")
		my_input = {
			"title": "new task",
			"due_date": "2022-05-01",
			"status": "I",
		}
		response = self.user1client.post("/tasktracker/add/", my_input)
		all_tasks = Task.objects.all()
		self.assertEqual(len(all_tasks), 1)
		task_id = all_tasks[0].id

		self.user2client.login(username="user2",password="123456")
		response = self.user2client.post(f"/tasktracker/delete/{task_id}/")
		self.assertEqual(response.status_code, 404)
		response = self.user2client.delete(f"/tasktracker/delete/{task_id}/")
		self.assertEqual(response.status_code, 400)
		response = self.user2client.get(f"/tasktracker/delete/{task_id}/")
		self.assertEqual(response.status_code, 400)

		all_tasks = Task.objects.all()
		self.assertEqual(len(all_tasks), 1)
		


	def testPositiveValidation(self):
		# TODO
		pass

