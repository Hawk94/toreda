from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import redirect, render
from django.views.generic import TemplateView
from django.views import View
from requests_oauthlib import OAuth2Session

from .models import SalesforceCredential

from datetime import datetime

class SalesforceAuthView(LoginRequiredMixin, View):
    login_url = reverse_lazy('account_login')
    redirect_field_name = 'salesforce:oauth'

    def post(self, request, *args, **kwargs):
        callback_uri = settings.SALESFORCE_CALLBACK_URL
        auth_url = settings.SALESFORCE_BASE_URL + settings.SALESFORCE_AUTHORIZATION_URL
        oauth = OAuth2Session(client_id=settings.SALESFORCE_CONSUMER_KEY, redirect_uri='https://127.0.0.1:8000/salesforce/callback')
        authorization_url, state = oauth.authorization_url(auth_url)
        request.session['oauth_state'] = state
        return redirect(authorization_url)


class SalesforceCallbackView(LoginRequiredMixin, TemplateView):
    login_url = reverse_lazy('account_login')
    redirect_field_name = 'salesforce:callback'
    template_name = 'salesforce/callback'

    def save_credentials(self, user, token):
        SalesforceCredential.objects.create(user=user,
                                            id_url=token['id'],
                                            issued_at=datetime.utcfromtimestamp(int(token['issued_at'])),
                                            scope=token['scope'],
                                            instance_url=token['instance_url'],
                                            token_type=token['token_type'],
                                            id_token=token['id_token'],
                                            signature=token['signature'],
                                            access_token=token['access_token'])

    def get(self, request, *args, **kwargs):
        token_url = settings.SALESFORCE_BASE_URL + settings.SALESFORCE_REQUEST_TOKEN_URL
        oauth = OAuth2Session(client_id=settings.SALESFORCE_CONSUMER_KEY, redirect_uri='https://127.0.0.1:8000/salesforce/callback')
        token = oauth.fetch_token(token_url, authorization_response=request.get_raw_uri(), client_secret=settings.SALESFORCE_CONSUMER_SECRET)
        self.save_credentials(request.user, token)
        return render(request, self.template_name)
