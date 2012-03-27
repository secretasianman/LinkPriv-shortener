from django.conf.urls.defaults import patterns, include, url
#from django.conf import settings

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('shortener.views',
    url(r'^$', 'index'),
    url(r'^submit/$','submit'),
    url(r'^batch/$','batchAnalysis'),
    url(r'^batchSubmit/$','batchSubmit'),
    url(r'^batchProcess/$','batchProcess'),
    url(r'^(?P<encoded>[a-zA-Z0-9]+)/$', 'redir'),
    
)
