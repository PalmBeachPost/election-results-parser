import requests

import configuration     # local file

import csv
from collections import OrderedDict

cleaningsheet = configuration.cleaningsheet
cleaningtemp = configuration.cleaningtemp
cleaningdone = configuration.cleaningdone
resultscomposite = configuration.resultscomposite

# Sample sheet:
# https://docs.google.com/spreadsheets/d/1X8gn-hp9qCNYNJuzCEi4E6d-kT9XvXmIWiwMdN7lA00/edit?usp=sharing
# Sample URL, then:
# https://docs.google.com/spreadsheets/d/1X8gn-hp9qCNYNJuzCEi4E6d-kT9XvXmIWiwMdN7lA00/export?format=csv
cleaningsheeturl = "https://docs.google.com/spreadsheets/d/" + cleaningsheet + "/export?format=csv"
with open(cleaningtemp, "wb") as f:
    f.write(requests.get(cleaningsheeturl).content)

with open(cleaningtemp, "r") as f:
    cleaningtemp = list(csv.DictReader(f))

spikedict = OrderedDict()
cleaning = OrderedDict()
for row in cleaningtemp:
    raceid = row['raceid']
    candidateid = row['candidateid']
    if raceid not in spikedict:
        spikedict[raceid] = []
    if row['spikerace'] == "y":
        spikedict[raceid].append("ALL")
    if row['spikepol'] == "y":
        spikedict[raceid].append(candidateid)
    if raceid not in cleaning:
        cleaning[raceid] = OrderedDict()
    if candidateid not in cleaning[raceid]:
        cleaning[raceid][candidateid] = row

with open(resultscomposite, "r") as f:
    masterlist = list(csv.DictReader(f))

localmatches = ["first", "last", "party", "incumbent", "runoff", "winner"]
racematches = ["officename", "seatname", "seatnum"]

with open(cleaningdone, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(list(masterlist[0].keys()))     # Write out header row in same Elex format
    for row in masterlist:
        raceid = row["raceid"]
        candidateid = row["candidateid"]
        if raceid not in cleaning:
            print("raceid " + raceid + " not found in list of cleaned races. Adding anyway.")
            writer.writerow(list(row.values()))
        elif "ALL" not in spikedict[raceid]:
            if candidateid not in cleaning[raceid]:
                print("candidateid " + candidateid + " not found in list of cleaned races. Adding anyway.")
                writer.writerow(list(row.values()))
            elif candidateid not in spikedict[raceid]:   # Someone we know about and want? No way!
                cleanrow = cleaning[raceid][candidateid]
                keyrow = cleaning[raceid][next(iter(cleaning[raceid]))]
                for item in localmatches:     # Match candidate-level name fixes
                    row[item] = cleanrow[item]
                for item in racematches:      # Match race-level fixes by getting 'em from first entry
                    row[item] = keyrow[item]
                writer.writerow(list(row.values()))
