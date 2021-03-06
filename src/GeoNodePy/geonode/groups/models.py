import datetime
import itertools

from django.conf import settings
from django.core.mail import send_mail
from django.db import models, IntegrityError
from django.template.loader import render_to_string
from django.utils.hashcompat import sha_constructor
from django.utils.translation import ugettext_lazy as _

from django.contrib.auth.models import User
from django.contrib.sites.models import Site

from django.core.urlresolvers import reverse

from taggit.managers import TaggableManager

from actstream.actions import follow, unfollow


class Group(models.Model):
    
    title = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)
    logo = models.FileField(upload_to="people_peoplegroup", blank=True)
    description = models.TextField()
    keywords = TaggableManager(_('keywords'), help_text=_("A space or comma-separated list of keywords"), blank=True)
    access = models.CharField(max_length=15, choices=[
        ("public", "Public"),
        ("public-invite", "Public (invite-only)"),
        ("private", "Private"),
    ])

    def __unicode__(self):
        return self.title
    
    def member_queryset(self):
        return self.groupmember_set.all()
    
    def user_is_member(self, user):
        if not user.is_authenticated():
            return False
        return user.id in self.member_queryset().values_list("user", flat=True)
    
    def user_is_role(self, user, role):
        if not user.is_authenticated():
            return False
        return self.member_queryset().filter(user=user, role=role).exists()
    
    def can_view(self, user):
        if self.access == "private":
            return user.is_authenticated() and self.user_is_member(user)
        else:
            return True
    
    def can_invite(self, user):
        if not user.is_authenticated():
            return False
        return self.user_is_role(user, "manager")
    
    def join(self, user, **kwargs):
        GroupMember(group=self, user=user, **kwargs).save()
        # Automatically follow a group when joining it.
        follow(user, self)
    
    def leave(self, user, **kwargs):
        GroupMember.objects.get(group=self, user=user, **kwargs).delete()
        unfollow(user, self)
    
    def invite(self, user, from_user, role="member", send=True):
        params = dict(role=role, from_user=from_user)
        if isinstance(user, User):
            params["user"] = user
            params["email"] = user.email
        else:
            params["email"] = user
        bits = [
            settings.SECRET_KEY,
            params["email"],
            str(datetime.datetime.now()),
            settings.SECRET_KEY
        ]
        params["token"] = sha_constructor("".join(bits)).hexdigest()
        
        # If an invitation already exists, re-use it.
        try:
            invitation = self.invitations.create(**params)
        except IntegrityError:
            invitation = self.invitations.get(group=self, email=params["email"])
        
        if send:
            invitation.send(from_user)
        return invitation

    def get_absolute_url(self):
        """Construct the absolute URL for this Item."""
        return reverse('geonode.groups.views.group_detail', None, [str(self.slug)])

class GroupMember(models.Model):
    
    group = models.ForeignKey(Group)
    user = models.ForeignKey(User)
    role = models.CharField(max_length=10, choices=[
        ("manager", "Manager"),
        ("member", "Member"),
    ])
    joined = models.DateTimeField(default=datetime.datetime.now)


class GroupInvitation(models.Model):
    
    group = models.ForeignKey(Group, related_name="invitations")
    token = models.CharField(max_length=40)
    email = models.EmailField()
    user = models.ForeignKey(User, null=True, related_name="pg_invitations_received")
    from_user = models.ForeignKey(User, related_name="pg_invitations_sent")
    role = models.CharField(max_length=10, choices=[
        ("manager", "Manager"),
        ("member", "Member"),
    ])
    state = models.CharField(
        max_length = 10,
        choices = zip(*itertools.tee([
            "sent",
            "accepted",
            "declined",
        ])),
        default = "sent",
    )
    created = models.DateTimeField(default=datetime.datetime.now)
    
    def __unicode__(self):
        return "%s to %s" % (self.email, self.group.title)

    class Meta:
        unique_together = [("group", "email")]
    
    def send(self, from_user):
        current_site = Site.objects.get_current()
        domain = unicode(current_site.domain)
        ctx = {
            "invite": self,
            "group": self.group,
            "from_user": from_user,
            "domain": domain,
        }
        subject = render_to_string("groups/email/invite_user_subject.txt", ctx)
        message = render_to_string("groups/email/invite_user.txt", ctx)
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [self.email])
    
    def accept(self, user):
        self.group.join(user, role=self.role)
        self.state = "accepted"
        self.user = user
        self.save()
    
    def decline(self):
        self.state = "declined"
        self.save()

