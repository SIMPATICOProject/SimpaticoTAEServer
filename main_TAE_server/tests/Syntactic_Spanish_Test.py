# -*- coding: utf-8 -*-

import urllib2

url = 'http://localhost:8080/?type=syntactic&sentence=Si%20la%20persona%20beneficiaria%20abandonase%20la%20estancia%20una%20vez%20iniciada%20,%20no%20tendrá%20derecho%20a%20ningún%20tipo%20de%20devolución%20.'

content = urllib2.urlopen(url).read()

print content
