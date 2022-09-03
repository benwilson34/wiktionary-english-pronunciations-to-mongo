import math
import time


startTime = None

def startTimer():
    global startTime 
    startTime = time.perf_counter()

def stopTimer():
    endTime = time.perf_counter()
    totalElapsedSeconds = endTime - startTime
    hours = math.trunc(totalElapsedSeconds / 3600)
    minutes = math.trunc((totalElapsedSeconds % 3600) / 60)
    secs = totalElapsedSeconds % 60
    return f'elapsed:  {hours:02.0f} : {minutes:02.0f} : {secs:06.3f} ({totalElapsedSeconds:.3f} sec)'
