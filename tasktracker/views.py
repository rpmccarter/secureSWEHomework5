from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponseNotFound, HttpResponseBadRequest
from django.shortcuts import render, reverse
from .models import Task
from django.db import connection
from django.core.exceptions import ValidationError

import logging

logger = logging.getLogger()

# View functions
def index(request):
	# checks whether user is authenticated
	if request.user.is_authenticated:
		# gets all tasks from the database
		task_list = Task.objects.filter(user=request.user) 
		# creates a dictionary to pass this list to the template file
		template_data = {'tasks': task_list}
		# renders the web page
		return render(request, 'index.html', template_data)
	else:
		logger.debug(f'unauthenticated request to {request.path} from {request.user}')
		return HttpResponseRedirect(reverse(f'login'))

# Adds a new task and redirect it back to index page
def add(request):
	if request.user.is_authenticated:
		# if the form was submitted
		if request.POST:
			title = request.POST['title']
			due_date = request.POST['due_date']
			status = request.POST['status']
			task = Task(user = request.user, title = title, due_date = due_date, status = status)
			# does input validation (full_clean() throws an exception if validation fails)
			try:
				task.full_clean() 
				# if no exception was thrown, form was validated
				# we proceed to save the task in the database

				# utilizes django's built-in object management to save to database
				# this prevents SQL injection attacks
				task.save()
				logger.info(f'user {request.user} created new task with id {task.id}')
			except ValidationError as e:
				# renders the web page again with an error message
				logger.error(f'user {request.user} attempted to create invalid task: {task}')
				return render(request, 'add.html', {"errors": e.message_dict})
				
			return HttpResponseRedirect(reverse(f'tasktracker:index'))
		else:
			# renders the web page
			logger.debug(f'invalid request method to {request.path} by {request.user}')
			return render(request, 'add.html')
	else:
		logger.debug(f'unauthenticated request to {request.path} from {request.user}')
		return HttpResponseRedirect(reverse(f'login'))


# Deletes a task (based on its primary key) and redirect it back to index page
def delete(request, pk):
	# requires user is authenticated
	if request.user.is_authenticated:

		# requires request is a POST so CSRF token is checked
		if request.method == 'POST':
			# uses ORM to delete the task
			try:
				task = Task.objects.get(id = pk)

				# checks task belongs to request sender before deletion
				if task.user == request.user:
					task.delete()
					logger.info(f'user {request.user} deleted task with id {pk}')
				else:
					logger.critical(f'user {request.user} attempting unauthorized delete of task with id {pk}')
					return HttpResponseNotFound()
			except Task.DoesNotExist as e:
				logger.error(f'user {request.user} attempting to delete nonexistent task with id {pk}')
				print(e)
				return HttpResponseNotFound()
			return HttpResponseRedirect(reverse(f'tasktracker:index'))
			# redirects user to index page
		else:
			logger.debug(f'invalid request method to {request.path} by {request.user}')
			return HttpResponseBadRequest()
	else:
		logger.debug(f'unauthenticated request to {request.path} from {request.user}')
		return HttpResponseRedirect(reverse(f'login'))