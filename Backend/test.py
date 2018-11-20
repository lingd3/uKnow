import urllib2
import urllib
# POST
data = urllib.urlencode({"praise":1, "user_id":1})
request = urllib2.Request('http://127.0.0.1:5000/api/questions/recommend',data)
response = urllib2.urlopen(request)
file = response.read()
print file
