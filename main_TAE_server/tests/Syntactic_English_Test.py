import urllib2

url = 'http://localhost:8080/?type=syntactic&sentence=His%20fighting%20technique%20is%20very%20unorthodox%20.'

content = urllib2.urlopen(url).read()

print content
