import email
import re
import requests 
import urlparse
import time
import random
import string
import whois
import dns.resolver
import jsonpickle
import os
import sys
from email.header import decode_header
from selenium import webdriver

# classes

class Sender():
    Name = ""
    Email = ""

    def __init__(self,pRaw):
        result = email.utils.parseaddr(pRaw)
        self.Name = result[0]
        self.Email = result[1]
    def __str__(self):
        name = ["-",self.Name][self.Name != ""]
        return "{0} <{1}>".format(name,self.Email)

class File(object):
    Name = ""
    Blob = None
    Mime = ""
    FullPath = ""

    def __str__(self):
        return "{0} ({1}): ".format(self.Name,self.Mime)

    __repr__ = __str__

class Mail(object):
    Subject=""
    Receiver=[],
    Sender=None
    Attachments=[]
    Body=""
    Mailer=""
    MessageID=""
    Server=[]
    Links=[]
    Trbwrk=""
    Hostname=""

    def __str__(self):
        response = "{0} => {1}: \"{2}\" ({3})".format(self.Sender,self.Receiver,self.Subject,self.Attachments) 
        return response

class Hyperlink(object):
    Url=""
    Status=404
    Whois={}
    Headers= {}
    Addresses=[]
    Screenshot=""
    Locations =None

    def __str__(self):
        
        if  "Server" not in self.Headers:
            self.Headers["Server"] = None

        if (self.Whois.name_servers == None):
            return "{0} (HTTP {1} {4}, {2}, {3})".format(self.Url,self.Status,self.Headers["Server"],self.Addresses,self.Screenshot);
        else:
            return "{0} (HTTP {1}, {7}, {8}, {9}, Location: {2}, {3} (*{4}), {5} ({6})".format(self.Url,self.Status,self.Whois.city,self.Whois.country,self.Whois.creation_date,self.Whois.name,self.Whois.emails,self.Headers["Server"],self.Addresses,self.Screenshot);

    __repr__ = __str__





class MailBD(object):
    """
        Mail Breakdown class, downloads, parses and analyses emails
    """

    trbwrkInstance = None

    failedHrefs = []
    def __init__(self,trbwrk):
        self.trbwrkInstance = trbwrk

    def getMail(self,raw):
        """ generate a Mail object from the source code and start analysis """
        msg = email.message_from_string(raw)
        got = Mail()
        got.Subject = self.getHeader(msg,"Subject")
        got.Sender = Sender(self.getHeader(msg,"From"))
        got.Receiver = self.getHeader(msg,"To")
        got.Body = self.getBody(msg)
        got.Mailer = self.getHeader(msg,"X-Mailer")
        got.MessageID = self.getHeader(msg,"Message-Id")
        got.Attachments = self.getAttachments(msg,got,False)
        got.Server = self.getServer(msg)
        got.Links = self.getLinks(got.Body)
        return got

    def getHeader(self,message,needle):
        """ extracts an header from the list and returns it """
        response = ""
        try:        
            decode = decode_header(message[needle])[0]
            response = unicode(decode[0])
        except(UnicodeDecodeError):
            response = message[needle] # in case of error -> return raw header instead of decoded them
        return response  

    def getBody(self,message):
        """ extracts the email body from the list and returns it """
        body = "";
        if (message.is_multipart()):
            for part in message.walk():
                mime = part.get_content_type()	
                if mime.find("text") != -1:	
                    body = part.get_payload(decode=True)
        else:
            body = message.get_payload(decode=True) 
        
        body = body.replace("\n","")
        return body

    def getAttachments(self,message,messageObj, addBlob=False):
        payload = []
        if (message.is_multipart()):
            for part in message.walk():
                mime = part.get_content_type()
                if part.get('Content-Disposition') is None:		
                    continue
                if mime.find("text") == -1:	
                    content = part.get_payload(decode=True)	
                    name = part.get_filename()
                    if (name != None):
                        att = File()
                        att.Name = name
                        att.Mime = mime
                        if addBlob:
                            att.Blob = content
                        
                        if (self.trbwrkInstance.attachmentFolder != "" and messageObj.MessageID != ""):  
                            folder = self.trbwrkInstance.attachmentFolder + "/" + messageObj.MessageID + "/"
                            path = self.trbwrkInstance.attachmentFolder + "/" + messageObj.MessageID + "/" + part.get_filename()   
                            if (os.path.isdir(folder) == False):
                                os.mkdir(folder)
                            if (self.trbwrkInstance.printHello):
                                print("Storing attachment to " + path)
                            fp = open(path, 'wb')		
                            fp.write(content)		
                            fp.close()
                            att.FullPath = path
                        payload.append(att)
        else:
            body = message.get_payload(decode=True) 
        
        return payload

    
    def getServer(self,message):
        results = []
        headers = message.get_all("Received")
        if (headers == None or len(headers) == 0):
            return "";
        
        for header in headers:
            try:
                if (header.startswith("from ")):
                    # is a from-header
                    index = header.index("by")
                    relevant = header[0:index]
                    # todo hostname detection
                    regex = re.compile(r"(?P<word>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}))")
                    for matches in re.findall(regex, relevant):
                        for m in matches:
                            if results.count(m) == -0:
                                results.append(m)
            except ValueError:
                pass
            except TypeError:
                pass
        return results

    def isLinkInList(self,list,href):
        if (len(list) == 0):
            return False
        for link in list:
            if (link.Url == href):
                return True
        return False

    def getLinks(self,body):
        links = []
        regex = re.compile(r"https?://[^ ^\"^\'^<]+")
        for match in re.findall(regex, body.replace("\n","").replace("\r","")):
            href = match;
            if (self.trbwrkInstance.doLinkVisit and self.isLinkInList(links,href) == False):
                try:
                    history = self.getRedirects(href)
                    for url in history:
                        domain = urlparse.urlparse(href)
                        hostname = domain.hostname;
                        if links.count(url.Url) == 0:
                            if (url.Status != 404 and self.trbwrkInstance.doScreenshots):
                                url.Screenshot = self.getScreen(url.Url)
                            if (self.trbwrkInstance.doWHOIS):
                                url.Whois = self.getWHOIS(hostname)
                            if (self.trbwrkInstance.doNSLOOKUP):
                                url.Addresses =  self.getIP(hostname)
                                url.Locations = []
                                for ip in url.Addresses:
                                    url.Locations.append(self.getLocation(ip))
                            links.append(url)
                except Exception,e:
                    print(e)
            else:
                if (self.isLinkInList(links,href) == False):
                    l = Hyperlink()
                    l.Url = href
                    l.Status = -1
                    l.Headers = []
                    links.append(l)
        return links

    def getRedirects(self, href):
        history = []
        try:
            if (href in self.failedHrefs):
                if (self.trbwrkInstance.printHello):
                    print("Skipping hyperlink, failed often")
                return []

            response = requests.get(href,timeout=self.trbwrkInstance.timeout)
            initial = Hyperlink()
            initial.Url = response.url
            initial.Status = response.status_code
            initial.Headers = self.getPlainHeaders(response.headers)
            history.append(initial)
            for resp in response.history:
                l = Hyperlink()
                l.Url = resp.url
                l.Status = resp.status_code
                l.Headers = self.getPlainHeaders(resp.headers)
                history.append(l)
        except Exception,e:
            self.failedHrefs.append(href)
            print(e)
        return history

    def getPlainHeaders(self,headers):
        plain = {}
        for header in headers.items():
            plain[header[0]] = header[1]
        return plain
    
    def getScreen(self,href):
        filename = ""
        try:
            driver = webdriver.PhantomJS()
            driver.set_window_size(1920, 1080) # set the window size that you need 
            driver.get(href)
            time.sleep(5)
            name = "".join(random.choice(string.lowercase) for i in range(8))
            filename = os.path.join(self.trbwrkInstance.screenshotFolder,name + '.png')
            driver.save_screenshot(filename)
            driver.quit()
        except Exception,e:
            print(e)
        return filename;
    
    def getWHOIS(self,hostname):
        data = {}
        try:
            data = whois.whois(hostname)
        except Exception,e:
            print("Error while getting whois informations")
        return data

    def getIP(self,hostname):
        addresses = [];
        records = ["A"]
        for record in records:
            if (hostname in self.failedHrefs):
                if (self.trbwrkInstance.printHello):
                    print("Skipping hyperlink, failed often")
                return []
            try:
                answers = dns.resolver.query(hostname, record)
                for ip in answers:
                    addresses.append(str(ip.address))
            except Exception, e:
                self.trbwrkInstance.failedHrefs.append(hostname)
                print (e)

        return addresses
    
    def getLocation(self,ip):
        response = requests.get("http://ip-api.com/json/"+ ip,timeout=self.trbwrkInstance.timeout)
        return jsonpickle.decode(response.text)