import requests

from .models import *

def is_following(host, id1, id2):
    try:
        if 'author/' in str(id2):
            id2 = id2.replace('https://', '').replace('http://', '')
        api_user = Site_API_User.objects.get(api_site__contains=host)
        api_url = api_user.api_site + "author/" + str(id1) + '/friends/' + str(id2)
        if not api_url.endswith('/'):
            api_url = api_url + '/'
        resp = requests.get(api_url, auth=(api_user.username, api_user.password))
        return json.loads(resp.content).get('friends')
    except Exception as e:
        # team4 connection
        try:
            if 'author/' in str(id2):
                id2 = [x for x in id2.split('/') if x][-1]
                
            api_user = Site_API_User.objects.get(api_site__contains=host)
            api_url = api_user.api_site + "author/" + str(id1) + '/friends/' + str(id2) + '/'
            resp = requests.get(api_url, auth=(api_user.username, api_user.password))
            return json.loads(resp.content).get('friends')
        except Exception as e:
            print("Error: authorization-friendschecking     " + str(e))
            pass
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
        if requestor.user.is_staff and not requestor.user.is_superuser:
            return False
        author = post.associated_author
        try:
            author.following.get(id=requestor.id)
            requestor.following.get(id=author.id)
            return True
        except:
            return False

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
            # Friend
            if middle.id == requestor.id:
                try:
                    requestor.following.get(id=author.id)
                    return True
                except:
                    pass

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
                    is_friend1 = is_following(middle.host, middle.id, requestor.url)
                    is_friend2 = is_following(middle.host, middle.id, author.url)
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
        return is_authorized_to_read_local_post(requestor, post) # Server-only posts will be transferred into local post authorization checking
    except Profile.DoesNotExist:
        pass

    # Remote comment author
    # Friends
    if post.visibility == 'FRIENDS':
        author = post.associated_author
        try:
            author.following.get(id=requestor_id)
            return is_following(host, requestor_id, author.url)
        except:
            return False

    # FOAF
    if post.visibility == "FOAF":
        author = post.associated_author
        for middle in author.following.all():
            if str(middle.id) == str(requestor_id): #Friend
                if is_following(host, requestor_id, author.url):
                    return True
                else:
                    continue

            # check if requestor is following middle friend
            if not is_following(host, requestor_id, middle.url):
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
                    api_user = Site_API_User.objects.get(api_site__contains=host)
                    is_friend1 = is_following(middle.host, middle.id, api_user.api_site+str(requestor_id))
                    is_friend2 = is_following(middle.host, middle.id, author.url)
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

    # Server Only -- serveronly post will be transferred into local_post authorization checking
    # if post['visibility'] == "SERVERONLY" and post['author']['host'] == requestor.host:
    #     return True

    try: #local post
        local_post = Post.objects.get(id=post['id'])
        return is_authorized_to_read_local_post(requestor, local_post)
    except: #remote post
        # Friends
        if post['visibility'] == 'FRIENDS':
            try:
                requestor.following.get(id=post['author']['id'])
                return is_following(post['author']['host'], post['author']['id'], requestor.url)
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
                        "id": requestor.url,
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

