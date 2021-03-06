from django.contrib.postgres.fields import JSONField
from django.db import models
from django.db.models import Q


class Invitations(models.Model):
    fxa_uid = models.CharField(max_length=255, blank=True)
    email = models.EmailField(db_index=True)
    date_added = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=False)
    date_sent = models.DateTimeField(null=True, blank=True)
    date_redeemed = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return 'Invitation for %s' % self.email


def get_invitation(email=None, fxa_uid=None, active=False):
    local_args = locals()
    invitations = Invitations.objects.filter(
        Q(email=email) | Q(fxa_uid=fxa_uid), active=active
    ).order_by('date_added')
    if invitations.count() < 1:
        raise Invitations.DoesNotExist(
            'get_invitation found no invitation for args: %s' % local_args
        )
    invitations = list(invitations)
    oldest_invitation = invitations.pop(0)
    for invite in invitations:
        if invite.email and oldest_invitation.email != invite.email:
            oldest_invitation.email = invite.email
        if  invite.fxa_uid and oldest_invitation.fxa_uid != invite.fxa_uid:
            oldest_invitation.fxa_uid = invite.fxa_uid
        invite.delete()
    oldest_invitation.save(update_fields=['email', 'fxa_uid'])
    return oldest_invitation


class MonitorSubscriber(models.Model):
    class Meta:
        db_table = 'subscribers'
        managed = False

    primary_email = models.CharField(max_length=255)
    fxa_uid = models.CharField(max_length=255)
    breaches_last_shown = models.DateTimeField()
    waitlists_joined = JSONField()
