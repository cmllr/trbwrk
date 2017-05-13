#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
from termcolor import colored, cprint
import json
import credentials
import sys
import getopt
import jsonpickle
import imaplib
import os

# Units
import mailBD

class trbwrk():
    """
      main entry point for trbwrk, starts actions by parsing the command line
    """
    seenMails = [] # list of analyzed mails
    seenMail = None # the analyzed mail
    printJSON = False # print output in json
    printHello = True # print version output
    doScreenshots = False # create screenshots?
    screenshotFolder = ""
    targetFile = ""
    doWHOIS = False # do whois queries
    timeout = 1
    attachmentFolder = "" # where to store attachments?
    doNSLOOKUP = False
    doLinkVisit = False
    def __init__(self):
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
                "json",
                "quiet",
                "screenshots=",
                "file=",
                "whois",
                "timeout=",
                "nslookup",
                "attachments=",
                "analyze",
                "visitlinks"
            ])
            self.parseCommandLine(options)
        except getopt.GetoptError:
            print("Use --help for more help")
            sys.exit(2)
    
    def parseCommandLine(self,options):
        """
            uses the results of getCommandLine to do some action
        """
        for o, a in options:
            if o in ("--json"):
                self.printJSON = True
            elif o in ("--quiet"):
                self.printHello = False
            elif o in ("--screenshots"):
                self.doScreenshots = True
                self.screenshotFolder = a
                if os.path.isdir(a) == False:
                    print("Screenshot folder does not exists")
                    sys.exit(5)
            elif o in ("--file"):
                self.targetFile = a
            elif o in ("--attachments"):
                self.attachmentFolder = a
            elif o in ("--timeout"):
                self.timeout = a
            elif o in ("--whois"):
                self.doWHOIS = True
            elif o in ("--nslookup"):
                self.doNSLOOKUP = True
            elif o in ("--visitlinks"):
                self.doLinkVisit = True
            elif o in ("--help"):
                self.printHelp()

        if (self.printHello and self.printJSON == False):
           print("trbwrk {0} © 2017 Christoph Müller <me@0fury.de>".format(self.getVersion()))

        for o, a in options:
            if o in ("--raw"):
                self.seenMail = self.parseMail(a);
                got = self.getJSON(self.seenMail,True);
                if (self.printJSON and self.targetFile != ""):
                    f = open(self.targetFile,"w+")
                    f.write(got)
                    f.close()
                elif (self.printJSON and self.targetFile == ""):
                    print(got)
                elif (self.printJSON == False and self.targetFile == ""):
                    print(self.seenMail);
            elif o in ("--honeypot"):
                self.seenMails = self.parseMails(credentials.SERVER,credentials.PORT,credentials.EMAIL,credentials.PASSWORD,credentials.FOLDER)
            


    def parseMail(self,path):
        fp = open(path)
        mbd = mailBD.MailBD(self)
        mail = mbd.getMail(fp.read())
        fp.close()
        mail.Trbwrk = self.getVersion()
        mail.Hostname = os.uname()[1]
        return mail
    

    def parseMails(self,server,port,emailaddr,password,folder):
        mails = []		
        mail = imaplib.IMAP4_SSL(server,port)		
        mail.login(emailaddr,password)		
        mail.select(folder);		
                
        rv, data = mail.search(None, "ALL") 		

        mbd = mailBD.MailBD(self)


        if (self.printJSON and self.targetFile != ""):
            if (os.path.isfile(self.targetFile)):
                os.remove(self.targetFile)
            
            identifier = data[0].split()
            for num in identifier:	
                rv, data = mail.fetch(num, '(RFC822)')		
                raw = data[0][1]		
                got = mbd.getMail(raw)	
                if (self.printHello):
                    print(got)
                
                got.trbwrk = self.getVersion()
                mails.append(got)	
                if (self.printJSON and self.targetFile != ""):
                    f = open(self.targetFile,"w")
                    f.write(self.getJSON(mails,True))
                    f.close()
                        
            
        return mails 
    
    def getJSON(self,what,pretty=False):
        json =  jsonpickle.encode(what,unpicklable=False,make_refs=False)

        if (pretty):
            from subprocess import Popen, PIPE, STDOUT
            p = Popen(['/usr/bin/jsonlint','-f'], stdout=PIPE, stdin=PIPE, stderr=PIPE)
            json = p.communicate(input=json)[0]
        return json

    def output(self,what):
        """
            prints out a given object (as JSON)
        """
        if self.printJSON:
            print(self.getJSON(what))
        else:
            print(what)


t = trbwrk()
sys.exit(2)