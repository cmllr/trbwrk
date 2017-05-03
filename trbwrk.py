import time
import imaplib
import email
import credentials

def get_mails():
    mail = imaplib.IMAP4_SSL(credentials.SERVER,credentials.PORT)
    mail.login(credentials.EMAIL,credentials.PASSWORD)
    mail.select("SPAM");
    type, data = mail.search(None,'ALL')
    mails = data[0].split();
    first = int(mails[0]);
    last = int(mails[-1]);
    for i in range(last, first,-1):
        type, mailBody =  mail.fetch(i,'(RFC822)')
        for response_part in mailBody:
            if isinstance(response_part,tuple):
                msg = email.message_from_string(response_part[1]);
                headers = msg.items();
get_mails()