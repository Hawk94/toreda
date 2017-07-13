from django.conf.urls import url

from . import views

urlpatterns = [
    url(
        regex=r'^$',
        view=views.SalesforceAuthView.as_view(),
        name='oauth'
    ),
    url(
        regex=r'^callback/$',
        view=views.SalesforceCallbackView.as_view(),
        name='callback'
    ),
]
