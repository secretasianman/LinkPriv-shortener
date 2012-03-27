from django.conf import settings
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.utils import simplejson
from django.test.client import Client

import itertools
import os.path
import threading
import MySQLdb

from models import Link,LinkSubmitForm,batchLinkSubmitForm,batchProcessorForm,checkURL
import webkit2png


def redir(request, encoded):
    #Potential shortened link. Decode and check to see if it's in the database. If so, redirect to full url page. If not, error.
    toRedirect = Link()
    findId = toRedirect.decode(encoded)

    try:
        check = Link.objects.get(id=findId)
    except Link.DoesNotExist:
        return HttpResponse("ERROR, YO")
    return HttpResponseRedirect(check.longUrl())



def submit(request):
    #Allow link input to create shortened link.
    link_form = LinkSubmitForm(request.POST)
    print(request.POST);
    
    if link_form.is_valid():
        url = link_form.cleaned_data['submitForm']
        
        #Arg Parse
        urlPart = url.partition('?')
        args = urlPart[2].split('&')
        
        combinations = []

        

        for i in range(0,len(args)+1):
            for perm in itertools.combinations(args,i):
                combinations.append(perm)
                
        print combinations
        
        count = 0

        #Image Gen
        for c in combinations:
            urlCombination = urlPart[0]+"?"
            for arg in c:
                urlCombination = urlCombination + arg +"&"
            urlCombination = urlCombination[0:len(urlCombination)-1]

            webkit2png.generate_image(urlCombination,
                                      os.path.join(settings.PROJECT_ROOT,
                                                   "media/ss_%d.png"%count))
            
        
            count = count + 1

        #Gets the shortened link if this url has been shortened already. If not, it makes a new one.
        link = None
        try:
            link = Link.objects.get(url = url)
        except Link.DoesNotExist:
            pass
        
        if link == None:
            new_link = Link(url = url)
            new_link.save()
            link = new_link
  
        return render_to_response('results.html',
                                  {"encodedLink": link.shortUrl(),
                                   "perm": simplejson.dumps(combinations)},
                                  context_instance=RequestContext(request))


def index(request):
    link_form = LinkSubmitForm()
    return render_to_response('index.html',
                              {'link_form': link_form},
                              context_instance=RequestContext(request))


#Batch Analysis Views

#Accepts a list of links to batch analyze. Separated by arbitrary separator, "|!|".
def batchAnalysis(request):
    inputs = batchLinkSubmitForm()
    return render_to_response('batch.html',
                              {'inputs': inputs},
                              context_instance=RequestContext(request))


#Takes a list of links and attempts to output the arg combination screenshots.
def batchSubmit(request):
    inputs = batchLinkSubmitForm(request.POST)
    print(request.POST);
    
    if(inputs.is_valid()):
        links = inputs.cleaned_data['links'].split("|!|")
        print links
        url = links[0]
        print url
        updatedLinks = inputs.cleaned_data['links'].replace(url+"|!|","")
        print updatedLinks

        invBatchProcessor = batchProcessorForm()

       
        #Arg Parse
        urlPart = url.partition('?')
        args = urlPart[2].split('&')
        
        combinations = []

        for i in range(0,len(args)+1):
            for perm in itertools.combinations(args,i):
                combinations.append(perm)
                
        print combinations
        
        count = 0

        #Image Gen
        for c in combinations:
            urlCombination = urlPart[0]+"?"
            for arg in c:
                urlCombination = urlCombination + arg +"&"
            urlCombination = urlCombination[0:len(urlCombination)-1]

            webkit2png.generate_image(urlCombination,
                                      os.path.join(settings.PROJECT_ROOT,
                                                   "media/ss_%d.png"%count))
            count = count + 1

            
        return render_to_response('batchResults.html',
                                      {"url" : url,
                                       "invBatchProcessor" : invBatchProcessor,
                                       "perm": simplejson.dumps(combinations),
                                       "links": updatedLinks},
                                      context_instance=RequestContext(request))

#Takes choices, current full link, and list of all input links.
#Uses choices and current full link to augment database.
#List of all input links is used to drive the batch analysis engine.
def batchProcess(request):
    inputs = batchProcessorForm(request.POST)
    
    if(inputs.is_valid()):
        url = inputs.cleaned_data['processingURL']
        unnecArgs = inputs.cleaned_data['choices']
        remainingLinks = inputs.cleaned_data['remainingLinks']

        #DB Connect to add unnecArgs.
        if(unnecArgs != ""):
            db = MySQLdb.connect(host='kozmo.cis.upenn.edu', user='dki', passwd='2U1ZWVmZ', db='twitter03')
            print "db connected"

            cursor=db.cursor()

            try:
                cursor.execute("update twitter_links set unnecArgs="+unnecArgs+" where expanded_link="+url)
                print "Successfully added unnec args to db: "+unnecArgs
            except:
                print "oh shiiiittttt. error."

            db.close()
        
        #Loop back to run with remaining links.
        c=Client()
        return c.post("/batchSubmit/", {'links':remainingLinks})
