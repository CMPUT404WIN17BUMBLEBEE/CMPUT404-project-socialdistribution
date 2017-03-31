import requests

from .models import *

def is_user1_following_user2(host, id1, id2):
    try:
        api_user = Site_API_User.objects.get(api_site__contains=host)
        api_url = api_user.api_site + "author/" + str(id1) + "/friends/" + str(id2) + '/'
        resp = requests.get(api_url, auth=(api_user.username, api_user.password))
        return json.loads(resp.content).get('friends')
    except:
        return False


def is_authorized_to_read_local_post(requestor, post):
    # Admin
    if requestor.user.is_superuser:
        return True
    # API user
    if requestor.user.is_staff:
        if post.visibility == 'SERVERONLY':
            return False
        return True
    # Public
    if post.visibility == "PUBLIC":
        return True
    # Own
    if post.associated_author == requestor:
        return True
    # Private
    if post.visibility == "PRIVATE" :
        if str(requestor.id) in post.visibleTo:
            return True
    # Server Only
    if post.visibility == "SERVERONLY" and post.associated_author.host == requestor.host:
        return True

    # Friends
    if post.visibility == 'FRIENDS':
        author = post.associated_author
        try:
            author.following.get(id=requestor.id)
            requestor.following.get(id=author.id)
            return True
        except:
            return False

    # FOAF
    if post.visibility == "FOAF":
        author = post.associated_author
        for middle in author.following.all():
            if middle.id == requestor.id: #Friend
                return True

            try: # check if requestor is following middle friend
                requestor.following.get(id=middle.id)
            except:
                continue

            try: # local middle author
                middle_author = Profile.objects.get(id=middle.id)
                try:
                    middle_author.following.get(id=author.id)
                    middle_author.following.get(id=requestor.id)
                    return True
                except:
                    continue
            except: # remote middle author
                try:
                    is_friend1 = is_user1_following_user2(middle.host, middle.id, requestor.id)
                    is_friend2 = is_user1_following_user2(middle.host, middle.id, author.id)
                    if is_friend1 and is_friend2:
                        return True
                except:
                    continue
    return False


def get_readable_local_posts(requestor, posts):
    posts = posts.filter(unlisted=False)
    queryset = Post.objects.none()
    for post in posts:
        if is_authorized_to_read_local_post(requestor, post):
            queryset = queryset | Post.objects.filter(id=post.id)
    print(queryset)
    return queryset.order_by("-published")


# post is a model object
def is_authorized_to_comment(requestor_id, post, host):
    # Public
    if post.visibility == "PUBLIC":
        return True
    # Private
    if post.visibility == "PRIVATE" :
        if str(requestor_id) in post.visibleTo:
            return True

    try: # local comment author
        requestor = Profile.objects.get(id=requestor_id)
        return is_authorized_to_read_local_post(requestor, post)
    except Profile.DoesNotExist:
        pass

    # Remote comment author
    # Friends
    if post.visibility == 'FRIENDS':
        author = post.associated_author
        try:
            author.following.get(id=requestor_id)
            return is_user1_following_user2(host, requestor_id, author.id)
        except:
            return False

    # FOAF
    if post.visibility == "FOAF":
        author = post.associated_author
        for middle in author.following.all():
            if str(middle.id) == str(requestor_id): #Friend
                if is_user1_following_user2(host, requestor_id, author.id):
                    return True
                else:
                    continue

            # check if requestor is following middle friend
            if not is_user1_following_user2(host, requestor_id, middle.id):
                continue

            try: # local middle author
                middle_author = Profile.objects.get(id=middle.id)
                try:
                    middle_author.following.get(id=author.id)
                    middle_author.following.get(id=requestor_id)
                    return True
                except Exception as e:
                    print(e)
                    continue
            except: # remote middle author
                try:
                    is_friend1 = is_user1_following_user2(middle.host, middle.id, requestor_id)
                    is_friend2 = is_user1_following_user2(middle.host, middle.id, author.id)
                    if is_friend1 and is_friend2:
                        return True
                except:
                    continue
    return False





# Authorization
def is_authorized_to_read_post(requestor, post):
    # Admin
    if requestor.user.is_superuser:
        return True
    # Public
    if post['visibility'] == "PUBLIC":
        return True
    # Own
    if str(post['author']['id']) == str(requestor.id):
        return True
    # Private
    if post['visibility'] == "PRIVATE" :
        if str(requestor.id) in post['visibleTo']:
            return True

    # Server Only
    if post['visibility'] == "SERVERONLY" and post['author']['host'] == requestor.host:
        return True

    try: #local post
        local_post = Post.objects.get(id=post['id'])
        return is_authorized_to_read_local_post(requestor, local_post)
    except: #remote post
        # Friends
        if post['visibility'] == 'FRIENDS':
            try:
                requestor.following.get(id=post['author']['id'])
                return is_user1_following_user2(post['author']['host'], post['author']['id'], requestor.id)
            except:
                return False
            
        # FOAF
        if post['visibility'] == "FOAF":
            try:
                api_user = Site_API_User.objects.get(api_site__contains=post['author']['host'])
                api_url = api_user.api_site + "posts/" + str(post['id']) + "/"
                data = {
                    "query": "getPost",
                    "postid": str(post['id']),
                    "url": api_url,
                    "author": {
                        "id": str(requestor.id),
                        "url": requestor.url,
                        "host": requestor.host,
                        "displayName": requestor.displayName,
                    },
                    "friends": [friend.url for friend in requestor.following.all()]
                }
                resp = requests.post(api_url, data=json.dumps(data), auth=(api_user.username, api_user.password),
                                     headers={'Content-Type': 'application/json'})
                if resp.status_code == 200:
                    return True
                else:
                    return False
            except:
                pass
    return False


def get_readable_posts(requestor, posts):
    results = list()
    for post in posts:
        if is_authorized_to_read_post(requestor, post):
            results.append(post)
    # Based on code from alecxe
    # http://stackoverflow.com/questions/26924812/python-sort-list-of-json-by-value
    results.sort(key=lambda k: k['published'], reverse=True)
    return results

