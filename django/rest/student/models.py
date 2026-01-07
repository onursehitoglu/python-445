from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Department(models.Model):
	'''Department model. contains department id and name fields'''
	did = models.CharField(max_length=10, primary_key = True)
	name = models.CharField(max_length=30)

class Course(models.Model):
	'''Course model. contains cid, name and prereq relation
       prereq relation is a many to many relation between Course
	  and itself
	'''
	cid = models.CharField(max_length=10, primary_key = True)
	name = models.CharField(max_length=100)
	prereq = models.ManyToManyField('self', symmetrical=False, blank=True)
	def __str__(self):
		return ':'.join([str(self.cid),str(self.name)])

	def addprereq(self, cid):
		'''Add a course as prerequisite of courses'''
		self.prereq.add(Course.objects.get(cid=cid))
	

class Student(models.Model):
	'''Student model. contains sid, name, surname,department (to Department)
	   in addition contains to many to many relations to course. took is
	   for courses already taken and passed. registered as the list of
		courses to register for this semester.
        user is a relation to django.contrib.auth.models.User to
		associate a user with the student
	'''
	sid = models.CharField(max_length=10, primary_key = True)
	name = models.CharField(max_length=30)
	surname = models.CharField(max_length=30)
	department = models.ForeignKey(Department,on_delete = models.CASCADE,blank=True, null=True)
	took = models.ManyToManyField(Course,related_name = 'taken')
	registered = models.ManyToManyField(Course,related_name = 'enrolled')
	user = models.OneToOneField(User, on_delete = models.CASCADE, null = True)

	def __str__(self):
		return ' '.join([str(self.sid),str(self.name),str(self.surname)])

	def add(self, cid):
		'''Add a course to students registration'''
		try:
			course = Course.objects.get(cid=cid)
			# already took?
			if course in self.registered.all():
				return {'registered': (course.cid, course.name) }
			# prerequsite check
			needstotake = []
			for c in course.prereq.all():
				if c not in self.took.all():
					needstotake.append((c.cid,c.name))
			if needstotake != []:
				return {'prereq': needstotake}

			# no section capacity check
			self.registered.add(course)
			return True
		except Exception as e:
			return {'error': str(e) }

	def drop(self, cid):
		'''Drop a course from students registration'''
		try:
			course = self.registered.get(cid=cid)
			self.registered.remove(course)
			return True
		except Exception as e:
			return {'error': str(e) }

	def canregister(self, course):
		'''test if student register a course'''
		for c in course.prereq.all():
			if c not in self.took.all():
				return False
		return True

	def coursestoregister(self):
		'''Generates a list of courses to register specific for student
		   not currently registered and all prerequisites are passed'''
		clist = []
		for course in Course.objects.exclude(cid__in = self.took.all()).exclude(cid__in = self.registered.all()):
			if self.canregister(course):
				clist.append(course)
		return clist
