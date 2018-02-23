import urllib2

url = 'http://localhost:8080/?type=lexical&target=sentencia&sentence=Esta%20es%20una%20sentencia%20.&index=3&lang=es'

content = urllib2.urlopen(url).read()

print content
