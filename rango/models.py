from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Category(models.Model):
	name = models.CharField(max_length = 128, unique = True)
	likes = models.IntegerField(default=0)
	views = models.IntegerField(default=0)

	def __unicode__(self):
		return self.name

class Page(models.Model):
	category = models.ForeignKey(Category)
	title = models.CharField(max_length = 128)
	url = models.URLField()
	views = models.IntegerField(default=0)

	def __unicode__(self):
		return self.title

class UserProfile(models.Model):
	# Required, links UserProfile to UserModel
	user = models.OneToOneField(User)

	# additional attributes
	website = models.URLField(blank = True)
	picture = models.ImageField(upload_to='profile_images', blank = True)

	# override unicode to return
	def __unicode__(self):
		return self.user.username