# Sample file for The Palm Beach Post and related papers. Tweak as you will.

import datetime
import os
from multiprocessing import Pool

scraperdir = "../florida-election-results"
parserdir = "../election-results-parser"

# parallelprocesses = ["Florida.py", "PalmBeach.py", "Miami-Dade.py"]

parallelprocesses = ["OH-Franklin.py"]

sequentialprocesses = ["composite_csvs.py", "middlewarepre.py", "middlewarepost.py", "app.py fml"]

def run_process(process):
    os.system('python {}'.format(scraperdir + "/" + process))
    
def timestamp():
    return(datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d %H:%M:%S"))

if __name__ ==  '__main__':
    print(f"Beginning run at {timestamp()}.")
    pool = Pool(processes=8)
    pool.map(run_process, tuple(parallelprocesses))
    pool.close()
    os.chdir("../election-results-parser")
    for script in sequentialprocesses:
        os.system('python {}'.format(script))
    print(f"Done processing at {timestamp()}.")
