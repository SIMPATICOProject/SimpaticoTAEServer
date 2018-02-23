# -*- coding: utf-8 -*-
import urllib2

url = 'http://localhost:8080/?type=lexical&target=collegamento&sentence=gestione%20dati%20del%20nucleo%20familiare%20in%20caso%20di%20casa%20famiglia%20(%20nucleo%20familiare%20)%20-%20da%20collegamento%20all’%20anagrafe%20.&index=16&lang=it'

content = urllib2.urlopen(url).read()
print content
