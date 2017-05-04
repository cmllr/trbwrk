import time
import credentials
from bootstrap import Bootstrap

b = Bootstrap()
  
print(b.Modules["mailAnalyse"].get_mails(credentials.SERVER,credentials.PORT,credentials.EMAIL,credentials.PASSWORD,credentials.FOLDER))