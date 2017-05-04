import imaplib
import email

class Mail:
    Subject=""
    Receiver=[],
    Sender=""
    Attachments={}
    def __init__(self,subject,receiver,sender,attachments):
        self.Subject = subject
        self.Receiver = receiver
        self.Sender = sender
        self.Attachments = attachments
    def toString(self):
        response = "{} => {}: \"{}\" {} attachments".format(self.Sender,self.Receiver,self.Subject,0) 
        return response


def getHeaderValue(headers,needle):
    for i in range(0,len(headers)):
        if (headers[i][0] == needle):
            return headers[i][1]
    return None


def get_mails(server,port,emailaddr,password,folder):
    mail = imaplib.IMAP4_SSL(server,port)
    mail.login(emailaddr,password)
    mail.select(folder);
    type, data = mail.search(None,'ALL')
    mails = data[0].split();
    first = int(mails[0]);
    last = int(mails[-1]);
    for i in range(last, first,-1):
        type, mailBody =  mail.fetch(str(i),'(RFC822)')
        for response_part in mailBody:
            if isinstance(response_part,tuple):
                msg = email.message_from_string(str(response_part[1]));
                headers = msg.items();
                attachments = {}
                if msg.is_multipart():
                    for part in msg.walk():
                        mime = part.get_content_type()
                        if part.get_content_maintype() == 'multipart':
                            continue
                        if part.get('Content-Disposition') is None:
                            continue
                        attachments[part.get_filename()] = part.get_payload(decode=True)
                        if part.get_filename() is not None:
                            fp = open("/run/media/chrism/497D-93DD/"+part.get_filename(), 'wb')
                            fp.write(part.get_payload(decode=True))
                            fp.close()
                else:
                    mime = msg.get_content_maintype()
                    body = msg.get_payload(decode=True)
                    #print(body)
                
                got = Mail(getHeaderValue(headers,"Subject"),getHeaderValue(headers,"To"),getHeaderValue(headers,"From"),{})
                print(got.toString())
        if i > 1:
            break