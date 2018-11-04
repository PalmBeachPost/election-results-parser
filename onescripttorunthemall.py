# Sample file for The Palm Beach Post and related papers. Tweak as you will.

import os
from multiprocessing import Pool

scraperdir = "../florida-election-results"
parserdir = "../election-results-parser"

parallelprocesses = ("Florida.py", "PalmBeach.py", "Miami-Dade.py")

sequentialprocesses = ["composite_csvs.py", "middlewarepre.py", "middlewarepost.py", "app.py fml"]

def run_process(process):
    os.system('python {}'.format(scraperdir + "/" + process))
    
if __name__ ==  '__main__':
    print("Beginning to scrape.")
    pool = Pool(processes=8)
    pool.map(run_process, parallelprocesses)
    pool.close()
    print("Done scraping")
    os.chdir("../election-results-parser")
    for script in sequentialprocesses:
        os.system('python {}'.format(script))
