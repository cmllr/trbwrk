import time
from termcolor import colored, cprint
import json
import credentials
import sys
from bootstrap import Bootstrap
import getopt
import jsonpickle

global b
b = Bootstrap()
  
mails = []
options = []
try:
    args = sys.argv[1:]
    options, args= getopt.getopt(args, 'abc:d:',[
        "help",
        "raw=",
        "honeypot",
        "json"
    ])
except getopt.GetoptError:
    print("hilfe")
    sys.exit(2)

outputInJSON = False
   
for o, a in options:
    if o in ("--raw"):
        fp = open(a)
        mail = b.Modules["MailHoneypot"].getMail(fp.read())
        mails.append(mail)
        fp.close()
    elif o in ("--honeypot"):
        mails = b.Modules["MailHoneypot"].getMails(credentials.SERVER,credentials.PORT,credentials.EMAIL,credentials.PASSWORD,credentials.FOLDER)
    elif o in ("--json"):
        outputInJSON = True
    elif o in ("--help"):
        print("help")
    else:
        assert False, "unhandled option"


extensions = {}
domains = {}

for mail in mails:

    mail.Links = b.Modules["LinkAnalyse"].getLinks(mail.Body)
    for link in mail.Links:
        if link in domains:
            domains[link] +=1
        else:
            domains[link] = 1
    attachments = []
    for at in mail.Attachments:
        extension = at.Name[at.Name.rfind("."):]
        if extension in extensions:
            extensions[extension] += 1
        else:
            extensions[extension] = 1
        attachments.append(at.Name)
    
    if (len(mail.Links) > 0 or len(mail.Attachments) > 0):
        time.sleep(1)
        if (outputInJSON):
            print(jsonpickle.encode(mail,unpicklable=False,make_refs=False))
        else:
            print(mail)
            cprint(attachments,"red")
            cprint(mail.Links,"yellow")
