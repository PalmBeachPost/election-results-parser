import configuration            # local file

from dirsync import sync

import os

webpath = configuration.webpath

os.makedirs(webpath, exist_ok=True)     # Build the directory

sync("built/", webpath, "sync", purge=True)


# os.system('cp -pr built/* ' + webpath)      # copy files
# os.system('python snapshotparser.py')
