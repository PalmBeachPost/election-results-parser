from tqdm import tqdm

import sqlite3
import csv
import os
from collections import OrderedDict

datadir = "./snapshots/"
datafile = "resultscleaned.csv"
sqlfile = "results.sqlite"
raceidswanted = '"120000", "160000", "160800", "260890", "260260", "240180"'
targetcsv = "/var/www/html/elexhighlights/highlights.csv"
candidateswanted = [
    "Andrew Gillum (D)", "Bill Nelson (D)", 'Jim Bonfiglio (D)',
    'Matt Caldwell (R)', 'Mike Caruso (R)', 'Nicole Fried (D)',
    'Rick Scott (R)', 'Ron DeSantis (R)']

conn = sqlite3.connect(sqlfile)
c = conn.cursor()
c.execute("SELECT snapshot FROM snapshots;")
snapshotsraw = c.fetchall()
snapshots = []
for snapshotnametuple in snapshotsraw:
    snapshots.append(snapshotnametuple[0])

datasought = {}
for root, dirs, files in os.walk(datadir, topdown=False):
    for name in files:
        if name == datafile:
            localfile = os.path.join(root, name)
            localdir = root[len(datadir):]
            if localdir not in snapshots:
                datasought[localdir] = localfile

print("Identified " + str(len(datasought)) + " new snapshots.")

def process_snapshot(snapshot):
    global datasought
    filename = datasought[snapshot]
    sqlstring = "insert into snapshots values ('" + snapshot + "');"     # Save directory name to snapshots table, so we don't look here again
    c.execute(sqlstring)
    with open(filename, "r") as f:
        reader = list(csv.DictReader(f))
    for row in reader:
        row['filepath'] = snapshot
        row.move_to_end('filepath', last=False)
        line = list(row.values())
        c.execute("insert into results values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", line)

for snapshot in tqdm(datasought):
    process_snapshot(snapshot)

conn.commit()       # Save data that was just inserted

for snapshot in tqdm(datasought):        # Add into highlights reel
    sqlstring = """
    insert into highlights select lastupdated, raceid,
    first||" "||last||" ("||substr(party, 1, 1)||")" as candidatename,
    officename||" "||seatname as racename,
    sum(votecount) as votecount from results """
    sqlstring += " where filepath='" + snapshot + "' and raceid in (" + raceidswanted + ") "
    sqlstring += " group by lastupdated, raceid, candidatename, racename; "
    
    c.execute(sqlstring)
conn.commit()

headers = ["lastupdated", "raceid", "candidatename", "racename", "votecount"]
c.execute("SELECT * FROM highlights where lastupdated >= '2018-11-06T20:03:01' order by lastupdated asc;")
highlightsraw = c.fetchall()
masterdict = OrderedDict()
for row in highlightsraw:
    line = OrderedDict()
    for i, item in enumerate(headers):
        line[item] = row[i]
    if line['lastupdated'] not in masterdict:
        masterdict[line['lastupdated']] = OrderedDict()
        for candidate in candidateswanted:
            masterdict[line['lastupdated']][candidate] = ""
    if line['candidatename'] in candidateswanted:
        masterdict[line['lastupdated']][line['candidatename']] = line['votecount']

print("Writing CSV")
with open(targetcsv, "w", newline="") as f:
    writer = csv.writer(f, lineterminator="\r\n")
    row = ["lastupdated"]
    row.extend(candidateswanted)
    writer.writerow(row)
    for timestamp in masterdict:
        line = [timestamp]
        line.extend(list(masterdict[timestamp].values()))
        writer.writerow(line)           

conn.close()


# c.execute("create table snapshots (snapshot varchar);")

# executestring = """CREATE TABLE results (
#         filepath varchar,
#         id VARCHAR NOT NULL,
#         raceid VARCHAR NOT NULL,
#         racetype VARCHAR,
#         racetypeid BOOLEAN,
#         ballotorder DECIMAL NOT NULL,
#         candidateid VARCHAR NOT NULL,
#         description BOOLEAN,
#         delegatecount BOOLEAN,
#         electiondate DATE,
#         electtotal DECIMAL NOT NULL,
#         electwon BOOLEAN,
#         fipscode BOOLEAN,
#         first VARCHAR,
#         incumbent BOOLEAN,
#         initialization_data BOOLEAN,
#         is_ballot_measure BOOLEAN,
#         last VARCHAR,
#         lastupdated TIMESTAMP,
#         level VARCHAR,
#         national BOOLEAN,
#         officeid BOOLEAN,
#         officename VARCHAR NOT NULL,
#         party VARCHAR,
#         polid VARCHAR,
#         polnum BOOLEAN,
#         precinctsreporting DECIMAL NOT NULL,
#         precinctsreportingpct DECIMAL NOT NULL,
#         precinctstotal DECIMAL NOT NULL,
#         reportingunitid VARCHAR NOT NULL,
#         reportingunitname VARCHAR NOT NULL,
#         runoff BOOLEAN,
#         seatname VARCHAR,
#         seatnum BOOLEAN,
#         statename VARCHAR,
#         statepostal VARCHAR,
#         test BOOLEAN,
#         uncontested BOOLEAN,
#         votecount DECIMAL NOT NULL,
#         votepct DECIMAL NOT NULL,
#         winner BOOLEAN);"""
# c.execute(executestring)
