import os

def populate():
	python_cat = add_cat(name='Python',
		likes = 64,
		views = 128)

	add_page(cat=python_cat,
		title="Official Python Tutorial",
		url="http://www.docs.python.org/2/tutorial/")

	add_page(cat=python_cat,
		title="How to Think like a Computer Scientist",
		url="http://www.greenteapress.com/thinkpython/")

	add_page(cat=python_cat,
		title="Learn Python in 10 Minutes",
		url="http://www.korokithakis.net/tutorials/python/")

	django_cat = add_cat('Django',
		likes = 32,
		views = 64)

	add_page(cat=django_cat,
		title="Official Django Tutorial",
		url="https://docs.djangoproject.com/en/1.5/intro/tutorial01/")

	add_page(cat=django_cat,
		title="Django Rocks",
		url="http://www.djangorocks.com/")

	add_page(cat=django_cat,
			title="How to Tango with Django",
			url="http://www.tangowithdjango.com/")

	frame_cat = add_cat("Other Frameworks",
		likes = 16,
		views = 32)

	add_page(cat=frame_cat,
		title="Bottle",
		url="http://bottlepy.ord/docs/dev/")

	add_page(cat=frame_cat,
			title="Flask",
			url="http://flask.pocoo.org/")

	# Print out what we have for the user
	for c in Category.objects.all():
		for p in Page.objects.filter(category=c):
			print "- {0} - {1}".format(str(c), str(p))

def add_page(cat, title, url, views = 0):
	p = Page.objects.get_or_create(category = cat, title = title, url = url)[0]
	return p

def add_cat(name, likes, views):
	c = Category.objects.get_or_create(name=name, likes=likes, views = views)[0]
	return c

# Start execution here
if __name__ == '__main__':
	print "Starting Rango population script..."
	os.environ.setdefault('DJANGO_SETTINGS_MODULE','tango_with_django_project.settings')
	from rango.models import Category, Page
	populate()