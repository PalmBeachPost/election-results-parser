import configuration    # configuration.py, with user-defined variables.

import csv
import glob

datadir = configuration.datadir
resultscomposite = configuration.resultscomposite

lineheaders = ["id", "raceid", "racetype", "racetypeid", "ballotorder", "candidateid", "description",
               "delegatecount", "electiondate", "electtotal", "electwon", "fipscode", "first", "incumbent",
               "initialization_data", "is_ballot_measure", "last", "lastupdated", "level", "national",
               "officeid", "officename", "party", "polid", "polnum", "precinctsreporting", "precinctsreportingpct",
               "precinctstotal", "reportingunitid", "reportingunitname", "runoff", "seatname",
               "seatnum", "statename", "statepostal", "test", "uncontested", "votecount", "votepct", "winner"
               ]

sourcecsvs = sorted(list(glob.glob(datadir + "*")))
masterlist = []
for filename in sourcecsvs:
    try:
        with open(filename, "r") as csvfile:
            reader = list(csv.DictReader(csvfile))
        if list(reader[0].keys()) != lineheaders:
            print("CSV input file " + filename + " has different headers than we're looking for. Not importing.")
        else:
            print("CSV input file " + filename + " seems to fit Elex standard. Importing.")
            for row in reader:
                masterlist.append(row)
    except:
        print(f"Something weird happened with {filename}.")
with open(resultscomposite, "w", newline="") as compositefile:
    writer = csv.writer(compositefile)
    writer.writerow(lineheaders)
    for row in masterlist:
        writer.writerow(list(row.values()))

