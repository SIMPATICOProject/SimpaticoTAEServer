# -*- coding: utf-8 -*-
import urllib2

url = 'http://localhost:8080/?type=lexical&target=medran&sentence=Os%20líquens%20que%20medran%20no%20residuo%20asfáltico%20suxiren%20a%20sua%20.&index=3&lang=gl'

content = urllib2.urlopen(url).read()
print content
