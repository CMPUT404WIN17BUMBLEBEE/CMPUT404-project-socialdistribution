from django.shortcuts import render
from datetime import datetime, timedelta
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import Context, loader
from .models import Post, Comment
from posts.forms import PostForm, CommentForm
from django.core.urlresolvers import reverse

# Create your views here.

#parts of code from http://pythoncentral.io/writing-simple-views-for-your-first-python-django-application/

def index(request):
	two_days_ago = datetime.utcnow() - timedelta(days=2)

	latest_posts_list = Post.objects.filter(date_created__gt=two_days_ago).all()

	#template = loader.get_template('index.html')

	context = {
	
	'latest_posts_list': latest_posts_list

	}

	return render(request, 'posts/index.html', context)

#code from http://pythoncentral.io/writing-simple-views-for-your-first-python-django-application/

def post_detail(request, post_id):
    try:
        post = Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
        # If no Post has id post_id, we raise an HTTP 404 error.
        raise Http404

    comment = Comment.objects 
    try:
        # currently only works for a post that does not have more than 1 comment
        comment = Comment.objects.get(associated_post=post_id)
    except Comment.DoesNotExist:
        # no comment for post, return 'no comments'
        comment.comment = "no comments"

    return render(request, 'posts/detail.html', {'post': post, 'comment': comment})

def add_comment(request, post_id):

    post = Post.objects.get(pk=post_id)

    if request.method == 'GET':
        form = CommentForm()
    else:
        form = CommentForm(request.POST)

        if form.is_valid():
            comment_text = form.cleaned_data['comment']
            date_created = form.cleaned_data['date_created']
            comment = Comment.objects.create(comment=comment_text, date_created=date_created, associated_post=post)

            return HttpResponseRedirect(reverse('post_detail', kwargs={'post_id': post.id})) 

    return render(request, 'posts/add_comment.html', {'form': form, 'post': post})
    

#code from http://pythoncentral.io/how-to-use-python-django-forms/
 
def post_form_upload(request):
    if request.method == 'GET':
        form = PostForm()
    else:
        # A POST request: Handle Form Upload
        form = PostForm(request.POST) # Bind data from request.POST into a PostForm
 
        # If data is valid, proceeds to create a new post and redirect the user
        if form.is_valid():
            posted_text = form.cleaned_data['posted_text']
            date_created = form.cleaned_data['date_created']
            post = Post.objects.create(posted_text=posted_text,
                                         date_created=date_created)
            return HttpResponseRedirect(reverse('post_detail',
                                                kwargs={'post_id': post.id}))
 
    return render(request, 'posts/post_form_upload.html', {
        'form': form,
    })






#again parts of code from
#http://pythoncentral.io/writing-views-to-upload-posts-for-your-first-python-django-application/
# NOT WORKING
def post_upload(request):
	if request.method =='GET':

		two_days_ago = datetime.utcnow() - timedelta(days=2)

		latest_posts_list = Post.objects.filter(date_created__gt=two_days_ago).all()

		#template = loader.get_template('index.html')

		context = {
	
		'post_upload': latest_posts_list

		}

		return render(request, 'posts/upload.html', context)
	elif request.method == 'POST':
		#fix after GET is working...
		post = models.Post.objects.create(content=request.POST['posted_text'],
			date_created=datetime.utcnow() )
		return HttpResponseRedirect(reverse('post_detail', kwargs={'post_id': post.id}))
