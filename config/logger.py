
from datetime import datetime
def loggingWrite(log, contact):
    f = open("Logging.txt", "a+")
    f.write(str(datetime.now().strftime("%b-%d-%Y %X")) + " - " + contact + " - " + log + "\n")
    f.close()
