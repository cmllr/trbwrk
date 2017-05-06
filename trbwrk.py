#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
from termcolor import colored, cprint
import json
import credentials
import sys
from bootstrap import Bootstrap
import getopt
import jsonpickle

# Units
import mailBD

class trbwrk():
    """
      main entry point for trbwrk, starts actions by parsing the command line
    """
    SeenMails = []
    """
      main entry point for trbwrk, starts actions by parsing the command line
    """
    def __init__(self):
        print("trbwrk {0} © 2017 Christoph Müller <me@0fury.de>".format(self.getVersion()))
        self.getCommandLine()

    def getVersion(self):
        """
            returns the git commit version or tag 
        """
        import subprocess
        from subprocess import check_output
        version = check_output(["/usr/bin/git", "describe","--always"])
        return version.replace("\n","")
    
    def printHelp(self):
        """
            prints a help text
        """
        print("this is a help text!")

    def getCommandLine(self):
        """
            parses the given commandline and calls parseCommandLine(options) for further calculation
        """
        try:
            args = sys.argv[1:]
            options, args= getopt.getopt(args, 'abc:d:',[
                "help",
                "raw=",
                "honeypot",
                "json"
            ])
            self.parseCommandLine(options)
        except getopt.GetoptError:
            self.printHelp()
            sys.exit(2)
    
    def parseCommandLine(self,options):
        """
            uses the results of getCommandLine to do some action
        """
        for o, a in options:
            if o in ("--raw"):
                self.parseMail(a)
            elif o in ("--honeypot"):
                mails = b.Modules["MailHoneypot"].getMails(credentials.SERVER,credentials.PORT,credentials.EMAIL,credentials.PASSWORD,credentials.FOLDER)
            elif o in ("--json"):
                outputInJSON = True
            elif o in ("--help"):
                self.printHelp()

    def parseMail(self,path):
        self.seenMails = []
        fp = open(path)
        mbd = mailBD.MailBD()
        mail = mbd.getMail(fp.read())
        self.seenMails.append(mail)
        fp.close()





t = trbwrk()
sys.exit(2)

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
