import urllib

from django import template
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from django.utils.hashcompat import md5_constructor
from django.core.urlresolvers import reverse

from avatar.models import get_primary_avatar
from avatar import AVATAR_DEFAULT_URL, AVATAR_GRAVATAR_BACKUP

register = template.Library()

def avatar_url(user, size=80):
    avatar = get_primary_avatar(user, size=size)
    if avatar:
        return avatar.avatar_url(size)
    else:
        if AVATAR_GRAVATAR_BACKUP:
            return "http://www.gravatar.com/avatar/%s/?%s" % (
                md5_constructor(user.email).hexdigest(),
                urllib.urlencode({'s': str(size)}),)
        else:
            return AVATAR_DEFAULT_URL
register.simple_tag(avatar_url)

def avatar(user, size=80):
    if not isinstance(user, User):
        try:
            user = User.objects.get(username=user)
            alt = unicode(user)
            url = avatar_url(user, size)
        except User.DoesNotExist:
            url = AVATAR_DEFAULT_URL
            alt = _("Default Avatar")
    else:
        alt = unicode(user)
        url = avatar_url(user, size)
    return """<img src="%s" alt="%s" width="%s" height="%s" />""" % (url, alt,
        size, size)
register.simple_tag(avatar)

def primary_avatar(user, size=80):
    """
    This tag tries to get the default avatar for a user without doing any db
    requests. It achieve this by linking to a special view that will do all the 
    work for us. If that special view is then cached by a CDN for instance,
    we will avoid many db calls.
    """
    alt = unicode(user)
    url = reverse('avatar_render_primary', kwargs={'user' : user, 'size' : size})
    return """<img src="%s" alt="%s" width="%s" height="%s" />""" % (url, alt,
        size, size)
register.simple_tag(primary_avatar)

def render_avatar(avatar, size=80):
    if not avatar.thumbnail_exists(size):
        avatar.create_thumbnail(size)
    return """<img src="%s" alt="%s" width="%s" height="%s" />""" % (
        avatar.avatar_url(size), str(avatar), size, size)
register.simple_tag(render_avatar)
