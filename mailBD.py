import email
import re
from email.header import decode_header

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

    def __str__(self):
        return "{0}: ".format(self.Name)

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

class MailBD(object):
    """
        Mail Breakdown class, downloads, parses and analyses emails
    """
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
        got.Attachments = self.getAttachments(msg)
        got.Server = self.getServer(msg)
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
                    body = part.get_payload()
        else:
            body = message.get_payload() 
        return body.replace("\n","")

    def getAttachments(self,message):
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
                        att.Blob = content
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