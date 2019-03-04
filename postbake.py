import configuration            # local file

import os

webpath = configuration.webpath

os.makedirs(webpath, exist_ok=True)     # Build the directory
os.system('cp -pr built/* ' + webpath)      # copy files
# os.system('python snapshotparser.py')
