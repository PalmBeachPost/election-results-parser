import requests

import configuration     # local file

import csv
from collections import OrderedDict
import datetime
import os
import shutil
from copy import deepcopy

cleaningsheet = configuration.cleaningsheet
cleaningtemp = configuration.cleaningtemp
cleaningdone = configuration.cleaningdone
resultscomposite = configuration.resultscomposite
snapshotsdir = configuration.snapshotsdir
datadir = configuration.datadir

localmatches = ["first", "last", "party", "incumbent", "runoff", "winner"]
racematches = ["officename", "seatname", "seatnum"]
sheetpull = [
    "first", "last", "party", "incumbent",
    "runoff", "winner", "spikerace", "spikepol", "raceid", "candidateid"
    ]

timestamp = datetime.datetime.strftime(datetime.datetime.now(), 
"%Y%m%d-%H%M%S")

lastupdated = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%dT%H:%M:%S")

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
    try:
        raceid = row['raceid']
    except KeyError:
        print("***middlewarepost.py errored out on trying to set row['raceid']")
        print("***Double-check that you've set your correct Google Sheet ID.")
        print("***That's in configuration.py.")
        print("***BUT the error almost certainly is that your Google Sheet is not public.")
        print("***Open the Sheet, top-right corner Share, hit Get shareable link.")
        import os
        os.exit(1)
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

stub = OrderedDict([
    ('id', ''), ('raceid', ''), ('racetype', ''), ('racetypeid', ''), ('ballotorder', ''), ('candidateid', ''),
    ('description', ''), ('delegatecount', ''), ('electiondate', ''), ('electtotal', 0), ('electwon', ''),
    ('fipscode', ''), ('first', ''), ('incumbent', ''), ('initialization_data', ''),
    ('is_ballot_measure', ''), ('last', ''), ('lastupdated', ''), ('level', ''), ('national', ''),
    ('officeid', ''), ('officename', ''), ('party', ''), ('polid', ''), ('polnum', ''),
    ('precinctsreporting', 0), ('precinctsreportingpct', 0), ('precinctstotal', 0),
    ('reportingunitid', 'PLACEHOLDER'), ('reportingunitname', 'PLACEHOLDER'), ('runoff', ''),
    ('seatname', ''), ('seatnum', ''), ('statename', ''), ('statepostal', ''), ('test', ''),
    ('uncontested', ''), ('votecount', 0), ('votepct', 0), ('winner', '')
    ])

stub['lastupdated'] = lastupdated

placeholderlist = []
for raceid in cleaning:
    keyrow = cleaning[raceid][next(iter(cleaning[raceid]))]  # Take the first line for clean racename, spikerace, etc.
    for candidateid in cleaning[raceid]:
        if "ALL" not in spikedict[raceid] and candidateid not in spikedict[raceid]:  # If we want a candidate
            cleanrow = cleaning[raceid][candidateid]
            line = deepcopy(stub)
            for item in sheetpull:
                line[item] = cleanrow[item]
            for item in racematches:
                line[item] = keyrow[item]
            line['id'] = f"{line['raceid']}_{line['reportingunitid']}"
            placeholderlist.append(line)

with open(resultscomposite, "r") as f:
    masterlist = list(csv.DictReader(f))

brokenraces = []
with open(cleaningdone, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(list(masterlist[0].keys()))     # Write out header row in same Elex format
    for row in placeholderlist:
        writer.writerow(list(row.values()))
    for row in masterlist:
        raceid = row["raceid"]
        candidateid = row["candidateid"]
        if raceid not in cleaning:
            if raceid not in brokenraces:
                brokenraces.append(raceid)
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

# snapshotsdir = configuration.snapshotsdir
# datadir = configuration.datadir
shutil.copytree(datadir, snapshotsdir + timestamp)
shutil.copy2(cleaningdone, snapshotsdir + timestamp)
