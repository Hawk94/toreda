from toreda.users.models import User
from django.conf import settings
from django.db import models

from requests_oauthlib import OAuth2Session
from simple_salesforce import Salesforce

class SalesforceCredential(models.Model):
    user = models.OneToOneField(User, related_name="salesforce_credentials",
                                    null=True, on_delete=models.SET_NULL)
                                    
    id_url = models.CharField(max_length=255, null=True, blank=True)
    issued_at = models.DateTimeField(null=True, blank=True)
    scope = models.CharField(max_length=255, null=True, blank=True)
    instance_url = models.CharField(max_length=255, null=True, blank=True)
    token_type = models.CharField(max_length=255, null=True, blank=True)
    refresh_token = models.CharField(max_length=255, null=True, blank=True)
    id_token = models.CharField(max_length=1200, null=True, blank=True)
    signature = models.CharField(max_length=255, null=True, blank=True)
    access_token = models.CharField(max_length=255, null=True, blank=True)


class SalesforceQuery(models.Model):
    QUERY_TYPE_CHOICES = (
        ('OP', 'Opportunity'),
        )

    credential = models.ForeignKey(SalesforceCredential, on_delete=models.CASCADE)
    query_type = models.CharField(max_length=2, choices=QUERY_TYPE_CHOICES)

    def get_query(self, query):
        self.refresh_token()
        sf = Salesforce(instance=self.client.instance_url, session_id=self.client.access_token)
        return sf.query_all(query)

    def refresh_token(self):
        client = OAuth2Session(self.credential.id_url,
                               token=self.credential.id_token,
                               auto_refresh_url=settings.SALESFORCE_BASE_URL + settings.SALESFORCE_AUTHORIZATION_URL,
                               token_updater=token_saver)
    
    def token_updater(self, token):
        self.credential.issued_at = token['issued_at']
        self.credential.signature = token['signature']
        self.credential.access_toke = token['access_token']
        self.credential.save()

