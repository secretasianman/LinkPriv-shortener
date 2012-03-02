from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.utils import simplejson

import itertools
import threading

from shortener.models import Link, LinkSubmitForm
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
    
    if link_form.is_valid():
        url = link_form.cleaned_data['submitForm']
        
        #Arg Parse
        urlPart = url.partition('?')
        args = urlPart[2].split('&')
        
        combinations = []

        for i in range(1,len(args)+1):
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
                                      "/home/kevinsu/workspace/LinkPriv-shortener/media/ss_" + str(count) + ".png")
            
        
            count = count + 1

        print threading.enumerate()
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
