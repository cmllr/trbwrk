import imaplib
import email
from email.header import decode_header

class Sender(object):
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

    def __str__(self):
        attachmentString = "";
        if (len(self.Attachments) > 0):
            for at in self.Attachments:
                attachmentString += at.Name+","
        attachmentString = attachmentString.strip(",")
        response = "{0} => {1}: \"{2}\" {3} attachments ({4}), ID: {5}, Mailer: {6}".format(self.Sender,self.Receiver,self.Subject,len(self.Attachments),attachmentString,self.MessageID,self.Mailer) 
        return response
        

def getHeader(message,needle):
    response = ""
    try:        
        decode = email.header.decode_header(message[needle])[0]
        response = unicode(decode[0])
    except(UnicodeDecodeError):
        response = message[needle]
    return response

def getBody(message):
    body = "";
    if (message.is_multipart()):
        for part in message.walk():
            mime = part.get_content_type()	
            if mime.find("text") != -1:	
                body = part.get_payload(decode=True)
    else:
        body = message.get_payload(decode=True) 

    return body
        
def getAttachments(message):
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

def getMails(server,port,emailaddr,password,folder):

    mails = []
    mail = imaplib.IMAP4_SSL(server,port)
    mail.login(emailaddr,password)
    mail.select(folder);
    
    rv, data = mail.search(None, "ALL")    

    for num in data[0].split():
            rv, data = mail.fetch(num, '(RFC822)')

            msg = email.message_from_string(data[0][1])
            got = Mail()
            got.Subject = getHeader(msg,"Subject")
            got.Sender = Sender(getHeader(msg,"From"))
            got.Receiver = getHeader(msg,"To")
            got.Body = getBody(msg)
            got.Mailer = getHeader(msg,"X-Mailer")
            got.MessageID = getHeader(msg,"Message-Id")
            got.Attachments = getAttachments(msg)
            mails.append(got)
        
