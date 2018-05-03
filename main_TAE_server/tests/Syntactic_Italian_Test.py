# -*- coding: utf-8 -*-

import urllib2

url = 'http://localhost:8080/?type=syntactic&sentence=Paolo%20Gentiloni,%20primo%20ministro%20italiano,%20chiede%20una%20decisione%20chiara%20sulla%20legislatura%20.&lang=it'

content = urllib2.urlopen(url).read()

print content
