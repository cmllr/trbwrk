import re
import whois
import urlparse

class Hyperlink(object):
    Url=""
    Status=404
    Whois=""
    def __str__(self):
        return "jlfasjfsafj";

def getRedirects(href):
    import requests 
    history = []
    response = requests.get(href)
    initial = Hyperlink()
    initial.Url = response.url;
    initial.Status = response.status_code
    history.append(initial)
    for resp in response.history:
        l = Hyperlink()
        l.Url = resp.url
        l.Status = resp.status_code
        history.append(l)
    return history

def getWHOIS(href):
    data = ""
    domain = urlparse.urlparse(href)
    data = whois.query(str(domain.hostname))
    return data

def getLinks(body):
    links = []
    
    regex = re.compile(r"https?://[^ ^\"^\'^<]+")
    for match in re.findall(regex, body.replace("\n","").replace("\r","")):
        href = match;
        history = getRedirects(href)
        for url in history:
            if links.count(url.Url) == 0:
                url.Whois = getWHOIS(url.Url)
                links.append(url.Url)
    
    return links