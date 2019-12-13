from django.db import models

# Create your models here.
class Tag(models.Model):
	text = models.CharField(max_length = 50, primary_key = True)
	def __str__(self):
		return self.text

class Question(models.Model):
	qtitle = models.CharField(max_length=100)
	qtext = models.CharField(max_length=1024)
	tag = models.ManyToManyField(Tag)
	def __str__(self):
		return "{}: {}".format(self.id,self.qtitle)

class Reply(models.Model):
	rtext = models.CharField(max_length=1024)
	replyto = models.ForeignKey(Question)
	def __str__(self):
		return "{}[{}]: {}".format(self.id, self.replyto.id, self.rtext[:20])



