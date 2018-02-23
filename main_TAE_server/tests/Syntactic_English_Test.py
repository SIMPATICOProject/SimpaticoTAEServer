import urllib2

url = 'http://localhost:8080/?type=syntactic&sentence=These%20organisations%20have%20been%20checked%20by%20us%20and%20should%20provide%20you%20with%20a%20quality%20service%20.&lang=en'

content = urllib2.urlopen(url).read()

print content
