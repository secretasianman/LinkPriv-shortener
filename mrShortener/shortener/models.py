import datetime
import math

from django.db import models
from django.conf import settings
from django import forms


class Link(models.Model):
    url = models.URLField(verify_exists=True, unique=True)
    

    def shortUrl(self):
        return settings.SITE_BASE_URL + self.encode()

    def longUrl(self):
        return self.url

    def encode(self):
        encodingSet = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ";
        base = len(encodingSet);
        encoded = ""
        currVal = self.id

        while(currVal > 0):
            encoded = encoded + encodingSet[int(currVal%base)]
            currVal = math.floor(currVal/base)
        return encoded

    def decode(self,toDecode):
        encodingSet = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ";
        base = len(encodingSet);
        decoded = 0

        for i in range(len(toDecode)):
            decoded += (encodingSet.find(toDecode[i])) * math.pow(base, i)
        return decoded
         

    def __unicode__(self):
        return self.shortUrl() + ' : ' + self.longUrl()


class LinkSubmitForm(forms.Form):
    submitForm = forms.URLField(verify_exists=True,label='')
