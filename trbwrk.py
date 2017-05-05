import time
import credentials
from bootstrap import Bootstrap

b = Bootstrap()
  
mails = b.Modules["MailHoneypot"].getMails(credentials.SERVER,credentials.PORT,credentials.EMAIL,credentials.PASSWORD,credentials.FOLDER)


pritn(len(mails))