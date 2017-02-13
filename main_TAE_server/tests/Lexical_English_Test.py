import urllib2

url = 'http://localhost:8080/?type=lexical&target=unorthodox&sentence=His%20fighting%20technique%20is%20very%20unorthodox%20.&index=5'

content = urllib2.urlopen(url).read()

print content
