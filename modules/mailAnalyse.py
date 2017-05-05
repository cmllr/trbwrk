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

class Mail(object):
    Subject=""
    Receiver=[],
    Sender=None
    Attachments={}

    def __str__(self):
        response = "{0} => {1}: \"{2}\" {3} attachments".format(self.Sender,self.Receiver,self.Subject,0) 
        return response
        

def getHeader(message,needle):
    response = ""
    try:        
        decode = email.header.decode_header(message[needle])[0]
        response = unicode(decode[0])
    except(UnicodeDecodeError):
        response = message[needle]
    return response


def get_mails(server,port,emailaddr,password,folder):
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

            print(got)
