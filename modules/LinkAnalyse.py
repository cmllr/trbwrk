import re
import whois
import dns.resolver
import urlparse
import time
import random
import string

class Hyperlink(object):
    Url=""
    Status=404
    Whois={}
    Headers= {}
    Addresses=[]
    Screenshot=""

    def __str__(self):
        
        if  "Server" not in self.Headers:
            self.Headers["Server"] = None

        if (self.Whois.name_servers == None):
            return "{0} (HTTP {1} {4}, {2}, {3})".format(self.Url,self.Status,self.Headers["Server"],self.Addresses,self.Screenshot);
        else:
            return "{0} (HTTP {1}, {7}, {8}, {9}, Location: {2}, {3} (*{4}), {5} ({6})".format(self.Url,self.Status,self.Whois.city,self.Whois.country,self.Whois.creation_date,self.Whois.name,self.Whois.emails,self.Headers["Server"],self.Addresses,self.Screenshot);

    __repr__ = __str__

def getRedirects(href):
    import requests 
    history = []
    response = requests.get(href)
    initial = Hyperlink()
    initial.Url = response.url
    initial.Status = response.status_code
    initial.Headers = getPlainHeaders(response.headers)
    history.append(initial)
    for resp in response.history:
        l = Hyperlink()
        l.Url = resp.url
        l.Status = resp.status_code
        l.Headers = getPlainHeaders(resp.headers)
        history.append(l)
    return history

def getPlainHeaders(headers):
    plain = {}
    for header in headers.items():
        plain[header[0]] = header[1]

    return plain

def getWHOIS(hostname):
    data = {}
    data = whois.whois(hostname)
    return data

def getIP(hostname):
    addresses = [];
    records = ["A","AAAA"]
    for record in records:
        try:
            answers = dns.resolver.query(hostname, record)
            for ip in answers:
                addresses.append(str(ip.address))
        except:
            pass

    return addresses

def getScreen(url):
    from selenium import webdriver
    driver = webdriver.PhantomJS()
    driver.set_window_size(1920, 1080) # set the window size that you need 
    driver.get(url)
    time.sleep(5)
    name = "".join(random.choice(string.lowercase) for i in range(8))
    driver.save_screenshot('/tmp/screenshots/'+name+'.png')
    driver.quit()
    return '/tmp/screenshots/'+name+'.png';

def getLinks(body):
    links = []
    regex = re.compile(r"https?://[^ ^\"^\'^<]+")
    for match in re.findall(regex, body.replace("\n","").replace("\r","")):
        href = match;
        try:
            history = getRedirects(href)
            for url in history:
                domain = urlparse.urlparse(href)
                hostname = domain.hostname;
                if links.count(url.Url) == 0:
                    if (url.Status != 404):
                        url.Screenshot = getScreen(url.Url)
                    else:
                        print("Site 404..skipping screenshot")
                    url.Whois = getWHOIS(hostname)
                    url.Addresses = getIP(hostname)
                    links.append(url)
        except:
            print("Could not read links")
        
    return links