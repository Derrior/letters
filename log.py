import time

DEBUG = 0
INFO = 1
ERROR = 2

MinLogLevel = INFO
GetStr = {DEBUG : "DEBUG", INFO : "INFO", ERROR : "ERROR"}


class log:
    f = open("log.txt", "w")
    def __init__(self, log_level=INFO):
        time.clock()
        self.log_level = log_level

    def __lshift__(self, other):
        if (self.log_level >= MinLogLevel):
            self.f.write("[%s]\t%f".ljust(20, ' ') % (GetStr[self.log_level], time.clock()))
            self.f.write(str(other) + '\n')
        return self

DebugLog = log(DEBUG)
InfoLog = log(INFO)
ErrorLog = log(ERROR)
