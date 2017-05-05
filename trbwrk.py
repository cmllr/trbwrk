import time
from termcolor import colored, cprint
import json
import credentials
from bootstrap import Bootstrap

b = Bootstrap()
  
mails = b.Modules["MailHoneypot"].getMails(credentials.SERVER,credentials.PORT,credentials.EMAIL,credentials.PASSWORD,credentials.FOLDER)

extensions = {}
domains = {}

for mail in mails:
    print(mail)
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
    

    cprint(attachments,"red")
    cprint(links,"yellow")


fp = open("./extensions.json", 'wb')		 
fp.write(json.dumps(extensions))		
fp.close()

fp = open("./domains.json", 'wb')		 
fp.write(json.dumps(domains))		
fp.close()