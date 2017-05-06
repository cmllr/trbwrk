#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
from termcolor import colored, cprint
import json
import credentials
import sys
import getopt
import jsonpickle

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
    deepCheck = False # crawl links, attachments?
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
                "deepcheck"
            ])
            self.parseCommandLine(options)
        except getopt.GetoptError:
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
            elif o in ("--deepcheck"):
                self.deepCheck = True
            elif o in ("--help"):
                self.printHelp()

        if (self.printHello):
           print("trbwrk {0} © 2017 Christoph Müller <me@0fury.de>".format(self.getVersion()))

        for o, a in options:
            if o in ("--raw"):
                self.seenMail = self.parseMail(a);
            elif o in ("--honeypot"):
                mails = b.Modules["MailHoneypot"].getMails(credentials.SERVER,credentials.PORT,credentials.EMAIL,credentials.PASSWORD,credentials.FOLDER)
            

        self.printResults()

    def parseMail(self,path):
        fp = open(path)
        mbd = mailBD.MailBD()
        mail = mbd.getMail(fp.read())
        fp.close()
        if self.printHello and self.deepCheck:
            print("Performing deep check...")
        if self.deepCheck:
            self.doDeepCheck(mail)
        return mail
    
    def doDeepCheck(self,mail):
        mbd = mailBD.MailBD()
        mail.Links = mbd.getLinks(mail.Body)

    def printResults(self):
        if self.seenMail != None:
            self.output(self.seenMail)

        if len(self.seenMails) > 0:
            for mail in self.seenMails:
                self.output(mail)
    
    def output(self,what):
        """
            prints out a given object (as JSON)
        """
        if self.printJSON:
            print(jsonpickle.encode(what,unpicklable=False,make_refs=False))
        else:
            print(what)

t = trbwrk()
sys.exit(2)