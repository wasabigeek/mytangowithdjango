from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect
from rango.models import Category, Page, UserProfile
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
from datetime import datetime
from rango.bing_search import run_query

def encode_url(category_name_url):
	return category_name_url.replace(' ','_')

def decode_url(category_name_url):
	return category_name_url.replace('_',' ')

def get_category_list(max_results=0, starts_with=''):
	cat_list = []
	if starts_with:
		cat_list = Category.objects.filter(name__istartswith=starts_with)
	else:
		cat_list = Category.objects.all()

	if max_results > 0:
		if len(cat_list) > max_results:
			cat_list = cat_list[:max_results]

	for cat in cat_list:
		cat.url = encode_url(cat.name)
	return cat_list

def index(request):
	# Request the context of the request
	# The context contains information such as the client's machine details
	context = RequestContext(request)

	cat_list = get_category_list()
	top_5_cat = Category.objects.all().order_by('-likes')[:5]
	pages_list = Page.objects.order_by('-views')[:5]
	context_dict = {'cat_list': cat_list, 'top_5_cat':top_5_cat, 'pages': pages_list}

	# COOKIES
	if request.session.get('last_visit'):
		last_visit_time = request.session.get('last_visit')
		visits = request.session.get('visits', 0)

		if (datetime.now() - datetime.strptime(last_visit_time[:-7], "%Y-%m-%d %H:%M:%S")).days > 0:
			request.session['visits'] = visits + 1
			request.session['last_visit'] = str(datetime.now())
	else:
		request.session['last_visit'] = str(datetime.now())
		request.session['visits'] = 1

	return render_to_response('rango/index.html', context_dict, context)

def about(request):
	context = RequestContext(request)
	
	visit_count = request.session.get('visits','0')

	context_dict = {'visit_count': visit_count}
	return render_to_response('rango/about.html', context_dict, context)

def category(request, category_name_url):
	# Request our context from the request passed to use
	context = RequestContext(request)

	# Change underscores in the category name to spaces
	category_name = decode_url(category_name_url)
	context_dict = {'category_name':category_name}

	try:
		# If does not exist, returns DoesNotExist
		category = Category.objects.get(name = category_name)
		pages = Page.objects.filter(category = category)
		context_dict['pages'] = pages
		context_dict['category'] = category
		context_dict['category_name_url'] = category_name_url
	except Category.DoesNotExist:
		pass

	# add category list
	context_dict['cat_list'] = get_category_list()

	# handle search
	
	if request.method == 'POST':
		query = request.POST['query'].strip()

		if query:
			result_list = run_query(query)
			context_dict['result_list'] = result_list

	return render_to_response('rango/category.html', context_dict, context)

@login_required
def like_category(request):
	context = RequestContext(request)
	cat_id = None
	if request.method == 'GET':
		cat_id = request.GET['category_id']

	like = 0
	if cat_id:
		category = Category.objects.get(id=int(cat_id))
		if category:
			likes = category.likes + 1
			category.likes = likes
			category.save()

	return HttpResponse(likes)

def suggest_category(request):
	context = RequestContext(request)
	cat_list = []
	starts_with = ''
	if request.method == 'GET':
		starts_with = request.GET['suggestion']

	cat_list = get_category_list(8, starts_with)

	return render_to_response('rango/category_list.html', {'cat_list':cat_list}, context)

def track_url(request):
	context = RequestContext(request)
	page_id = None
	url = '/rango/'
	if request.method == 'GET':
		if 'page_id' in request.GET:
			page_id = request.GET['page_id']
			try:
				page = Page.objects.get(id = page_id)
				page.views += 1
				page.save()
				url = page.url
			except:
				pass
	return redirect(url)

@login_required
def add_category(request):
	context = RequestContext(request)

	# check if HTTP POST
	if request.method == 'POST': 
		form = CategoryForm(request.POST)

		# is form valid?
		if form.is_valid():
			# save new category to DB
			form.save(commit = True)

			# Now call the index() view
			# the user will be shown the homepage
			return index(request)
		else:
			# show errors to user
			print form.errors
	else:
		# If request was not POST, display form
		form = CategoryForm()

	return render_to_response('rango/add_category.html', {'form':form}, context)

@login_required
def add_page(request, category_name_url):
	context = RequestContext(request)

	category_name = decode_url(category_name_url)
	if request.method == 'POST':
		form = PageForm(request.POST)

		if form.is_valid():
			# Cannot save straightaway as not all fields are auto-populated
			page = form.save(commit = False)
			
			# retrieve Category object so we can add to it
			try:
				cat = Category.objects.get(name=category_name)
				page.category = cat
			except Category.DoesNotExist:
				return render_to_response('rango/add_category.html', {}, context)

			page.views = 0 # set default views

			page.save()

			return category(request, category_name_url) # display Category after saving
		else:
			print form.errors

	else:
		form = PageForm()

	return render_to_response('rango/add_page.html', 
		{'category_name_url':category_name_url,
		'category_name':category_name, 'form':form}, context)

@login_required
def auto_add_page(request):
	context = RequestContext(request)
	cat_id = None
	url = None
	title = None

	if request.method == "GET":
		cat_id = request.GET['category_id']
		url = request.GET['url']
		title = request.GET['title']

		if cat_id:
			category = Category.objects.get(id = int(cat_id))
			p = Page.objects.get_or_create(category = category, title = title, url = url)

	pages = Page.objects.filter(category = category).order_by('views')

	context_dict = {'pages':pages}
	return render_to_response('rango/page_list.html', context_dict, context)

def register(request):
	context = RequestContext(request)
	registered = False # True when reg. succeeds

	if request.method == 'POST':
		user_form = UserForm(data = request.POST)
		profile_form = UserProfileForm(data = request.POST)

		if user_form.is_valid() and profile_form.is_valid():
			user = user_form.save()
			user.set_password(user.password) # hash password
			user.save()

			# delay saving (commit = True) model until user is set
			profile = profile_form.save(commit = False) # just a temp object, not saved to DB
			profile.user = user

			if 'picture' in request.FILES:
				profile.picture = request.FILES['picture']
			
			profile.save()
			registered = True

		else:
			print user_form.errors, profile_form.errors


	else: # not POST, so render form using Model
		user_form = UserForm()
		profile_form = UserProfileForm()

	return render_to_response('rango/register.html',
		{'user_form':user_form, 'profile_form': profile_form, 'registered':registered},
		context)

def user_login(request):
	context = RequestContext(request)

	if request.method == 'POST':
		username = request.POST['username']
		password = request.POST['password']

		user = authenticate(username = username, password = password)

		if user is not None: # means successful
			if user.is_active:
				login(request, user)
				return HttpResponseRedirect('/rango/')
			else:
				return HttpResponse('Your Rango account is deactivated')
		else: # cannot find user object
			print "Invalid login details: {0}, {1}".format(username, password)
			return HttpResponse('Invalid login details.')

	else:
		return render_to_response('rango/login.html', {}, context)

@login_required
def restricted(request):
	return HttpResponse("Since you're logged in, you can see this text!")

@login_required # ensures only those logged in can view
def user_logout(request):
	logout(request)
	return HttpResponseRedirect('/rango')

@login_required
def profile(request):
	context = RequestContext(request)
	cat_list = get_category_list()

	context_dict = {'cat_list':cat_list}
	u = User.objects.get(username = request.user)

	try:
		up = UserProfile.objects.get(user = u)
	except:
		up = None

	context_dict['user'] = u
	context_dict['userprofile'] = up

	return render_to_response('rango/profile.html', context_dict, context)