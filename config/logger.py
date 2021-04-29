from datetime import datetime

logFileName = "data/Logging.txt"


def loggingWrite(log, contact):
    f = open(logFileName, "a+")
    f.write(str(datetime.now().strftime("%b-%d-%Y %X")) + " - " + contact + " - " + log + "\n")
    f.close()
