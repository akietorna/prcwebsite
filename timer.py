from time import localtime,strftime
from datetime import datetime

def converting_time(seconds):
    seconds = seconds % (24 * 3600) #takes care of the timing in seconds
    seconds %= 36000 
    minutes = seconds // 60
    seconds %=60