import configuration        # local file

import csv
from collections import OrderedDict

resultscomposite = configuration.resultscomposite
cleaningpre = configuration.cleaningpre
cleaningsheet = configuration.cleaningsheet
cleaningdone = configuration.cleaningdone

targets = ["officename", "seatname", "seatnum", "first", "last", "party", "incumbent", "runoff", "winner", "spikerace", "spikepol", "raceid", "candidateid"]
officenamesneverwanted = ["CDD"]
partiesneverwanted = ["Write-in", "Write-In", "WRITE-IN"]

masterlist = OrderedDict()
masterout = []
masterraces = OrderedDict()
with open(resultscomposite, "r") as f:
    masterlist = list(csv.DictReader(f))


def cleanline(line):
    for officename in officenamesneverwanted:
        if officename in line['officename']:
            line['spikerace'] = "y"
    for partyneverwanted in partiesneverwanted:
        if partyneverwanted == line['party']:
            line['spikepol'] = "y"
    return(line)


# Basic logic below:
# If we haven't seen this race before, we want one line with all the candidate and race info
# Like, one line with the office name and the first candidate. Subsequently, we want just the candidate info.

for row in masterlist:
    if row['raceid'] not in masterraces:
        masterraces[row['raceid']] = OrderedDict()
        line = OrderedDict()
        row['spikepol'], row['spikerace'] = ("", "")
        for item in targets:
            line[item] = row[item]   # Take everything, including officename
        line = cleanline(line)
        masterraces[row['raceid']][row['candidateid']] = line
    elif row['candidateid'] not in masterraces[row['raceid']]:
        row['spikepol'], row['spikerace'] = ("", "")
        line = OrderedDict()
        for item in targets[:3]:
            line[item] = ""
        for item in targets[3:]:
            line[item] = row[item]
        line = cleanline(line)
        masterraces[row['raceid']][row['candidateid']] = line

with open(cleaningpre, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(targets)
    for raceid in masterraces:
        for candidateid in masterraces[raceid]:
            row = masterraces[raceid][candidateid]
            writer.writerow(list(row.values()))
