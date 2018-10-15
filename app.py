# coding: utf-8
# Built for Python 3
"""
To-do list:
Move to external config file with list of papers, folder names
Do we sort by vote?
Implement county details
Move to dynamic data tables thingy?
Templatize route building
Build route for group pages
Build generator for group, main pages
Build out Frozen Flask
Add in Pym or Seattle iframe solution -> Can we test with GateHouse?
Build route for paper pages
Build template for paper pages



Allow resorting of group names, e.g., Governor, then U.S. Senate, then U.S. House?
Simplify party names when there are more (Green, Reform)
Build a system to identify winners
Figure out how to handle the "keep to retain" races
Cure cancer
Foment world peace

Done:
Build styles
Tag TD, TH elements

Votes not getting set under racedict[race]
Actually parse stuff
Clean up judicial shit
Build rounder tool; watch for zeroes
Build comma tool
Count votes at county-candidate and candidate levels

Not doing:
Calculate PrecinctRPct
Calculate candidate vote share
Build PrecinctsRPct into racedict-race-Counties-name, racedict-race-Candidates
Build Votes, VoteP into racedict-race-Candidates-name and racedict-race-Counties-name

"""
from flask import Flask, render_template, redirect, url_for, request   # External dependency
from flask_frozen import Freezer
from slugify import slugify # awesome-slugify, from requirements

import configuration    # configuration.py, with user-defined variables.

import csv
import glob
import time
import datetime
from collections import OrderedDict
import pprint
import os
import sys
from subprocess import Popen
import pickle



# primary = True
# datadir = "snapshots/"
# homedir = r'/root/data/florida-election-results'
# resultscomposite = "./resultscomposite.csv"   # Path to Final compiled CSV in Elex format, with data from all sources

#racedelim = " -- "    # E.g., "U.S. Senator -- Rep."

datadir = configuration.datadir
resultscomposite = configuration.resultscomposite
papers = configuration.papers

app = Flask(__name__)
freezer = Freezer(app)
pp = pprint.PrettyPrinter(indent=4)

def composite_csvs():
    global resultscomposite
    global datadir
    lineheaders = ["id", "raceid", "racetype", "racetypeid", "ballotorder", "candidateid", "description",
                   "delegatecount", "electiondate", "electtotal", "electwon", "fipscode", "first", "incumbent",
                   "initialization_data", "is_ballot_measure", "last", "lastupdated", "level", "national",
                   "officeid", "officename", "party", "polid", "polnum", "precinctsreporting", "precinctsreportingpct",
                   "precinctstotal", "reportingunitid", "reportingunitname", "runoff", "seatname",
                   "seatnum", "statename", "statepostal", "test", "uncontested", "votecount", "votepct", "winner"
                   ]
    
    sourcecsvs = list(glob.glob(datadir + "*"))
    masterlist = []
    for filename in sourcecsvs:
        with open(filename, "r") as csvfile:
            reader = list(csv.DictReader(csvfile))
        if list(reader[0].keys()) != lineheaders:
            print("CSV input file " + filename + " has different headers than we're looking for. Not importing.")
        else:
            print("CSV input file " + filename + " seems to fit Elex standard. Importing.")
            for row in reader:
                masterlist.append(row)
    with open(resultscomposite, "w", newline="") as compositefile:
        writer = csv.writer(compositefile)
        writer.writerow(lineheaders)
        for row in masterlist:
            writer.writerow(list(row.values()))


# folders = sorted(list(glob.glob(datadir + "*")), reverse=True)  # Find the latest time-stamped folder
# folder = folders[0] + "/"
# if not os.path.exists(folder + "done"):
    # time.sleep(10)   # Try to beat a race condition
    # if not os.path.exists(folder + "done"):
        # print(quit)


def get_timestamp():
    global folder
    rawtimestamp = folder.split("-")[1].replace("/", "")
    hour = int(rawtimestamp[0:2])
    pm = False
    if hour > 12:
        hour = hour -12
        pm = True
    if hour == 0:
        hour = 12
    hour = str(hour)
    timestamp = hour + ":" + rawtimestamp[2:4]
    if pm:
        timestamp = timestamp + " p.m."
    else:
        timestamp = timestamp + " a.m."
    return(timestamp)


@app.template_filter('comma')
def comma(input):
    return("{:,}".format(input))


@app.template_filter('pct')
def pct(incoming):
    if incoming == 0:
        result = 0
    else:
        result = round(100*float(incoming), 1)
    return(result)


@app.template_filter('slugifier')
def slugifier(text):
    return(slugify(text, to_lower=True))


def cleanrow(row):
    return(row)


composite_csvs()
    
with open(resultscomposite, "r") as f:    # Import the data and do some basic cleaning
    masterlist = []
    for row in csv.DictReader(f, delimiter="\t"):
        masterlist.append(cleanrow(row))


# with open("recastreport.csv", "w", newline="") as f:
    # headers = row.keys()
    # writer = csv.writer(f)
    # writer.writerow(headers)
    # for row in masterlist:
        # line = []
        # for item in headers:
            # line.append(str(row[item]))
        # writer.writerow(line)


# Translations:
# countydict -> reportingdict   with reportingunitname        
# racetracker ... was never used?
# racedict was built around the distinct racename, but that's perilous. Let's see:
#   -- Racedict should be done by raceid.
#   -- Racedict then needs a key for the race name; ordinarily officename, but may include
#       -- Party
#       -- Seatname
#       -- Seatnumber
#     ... so should that be parsed here or at the intermediate level? Seems like intermediate level.
#     because if we're grouping by raceid, then we don't care what the name is. Let's be agnostic.



        
reportingdict = OrderedDict()   # Holds reporting unit ID?
racedict = OrderedDict()
racenamegroups = OrderedDict()



for row in masterlist:
    # Begin basic setup
# OK, before reportingdict held countynames. The values were the names of races, which we wanted to be unique.
# Now we want reportingdict to hold reportingunitid (county IDs, not names).
# And instead of names of races we want the raceid, which must be unique.

    if row['reportingunitid'] not in reportingdict:
        reportingdict[row['reportingunitid']] = []
    if row['officename'] not in reportingdict[row['reportingunitid']]:
        reportingdict[row['reportingunitid']].append(row['raceid'])
    # if row['CountyName'] not in reportingdict:
        # reportingdict[row['CountyName']] = []
    # if row['FullRace'] not in reportingdict[row['CountyName']]:
        # reportingdict[row['CountyName']].append(row['FullRace'])
    
# OK, so we were going by racedict holding unique race names. We can't do that any more.
# So let's have racedict hold raceids , and the racename / officename will be a value.
    if row['raceid'] not in racedict:
        racedict[row['raceid']] = OrderedDict()
        for item in ["votecount", "precinctstotal", "precinctsreporting"]:
            racedict[row['raceid']][item] = 0
            racedict[row['raceid']]['officename'] = row['officename']
    # if row['FullRace'] not in racedict:
        # racedict[row['FullRace']] = OrderedDict()
        # for item in ["Votes", "Precincts", "PrecinctsR"]:
            # racedict[row['FullRace']][item] = 0
# Now, we want everything keyed to the reportingunitid instead of the county name, right?
        racedict[row['raceid']]['reportingunitid'] = OrderedDict()
        racedict[row['raceid']]['polid'] = OrderedDict()
        # racedict[row['FullRace']]['Counties'] = OrderedDict()
        # racedict[row['FullRace']]['Candidates'] = OrderedDict()
    if row['polid'] not in racedict[row['raceid']]['polid']:
        racedict[row['raceid']]['polid'][row['polid']] = {}
        racedict[row['raceid']]['polid'][row['polid']]['votecount'] = 0
        for item in ['first', 'last', 'party']:
            racedict[row['raceid']]['polid'][row['polid']][item] = row[item]
    # if row['FullName'] not in racedict[row['FullRace']]['Candidates']:
        # racedict[row['FullRace']]['Candidates'][row['FullName']] = {}
        # racedict[row['FullRace']]['Candidates'][row['FullName']]['Votes'] = 0
        # for item in ["CanNameLast", "CanNameMiddle", "CanNameFirst", "PartyName", "ShortParty"]:
            # racedict[row['FullRace']]['Candidates'][row['FullName']][item] = row[item]

            


    if row['CountyName'] not in racedict[row['FullRace']]['Counties']:
        racedict[row['FullRace']]['Counties'][row['CountyName']] = OrderedDict()
        racedict[row['FullRace']]['Counties'][row['CountyName']]['Candidates'] = OrderedDict()
        racedict[row['FullRace']]['Counties'][row['CountyName']]['PrecinctsR'] = row['PrecinctsReporting']
        racedict[row['FullRace']]['Counties'][row['CountyName']]['Precincts'] = row['Precincts']
        racedict[row['FullRace']]['Counties'][row['CountyName']]['Votes'] = 0
        racedict[row['FullRace']]['Precincts'] += row['Precincts']
        racedict[row['FullRace']]['PrecinctsR'] += row['PrecinctsReporting']
    if row['RaceNameGroup'] not in racenamegroups:
        racenamegroups[row['RaceNameGroup']] = []
    # if row['RaceName'] not in racenamegroups[row['RaceNameGroup']]:
    if row['FullRace'] not in racenamegroups[row['RaceNameGroup']]:
        # racenamegroups[row['RaceNameGroup']].append(row['RaceName'])
        racenamegroups[row['RaceNameGroup']].append(row['FullRace'])
    racedict[row['FullRace']]['Counties'][row['CountyName']]['Votes'] += row['CanVotes']
    racedict[row['FullRace']]['Candidates'][row['FullName']]['Votes'] += row['CanVotes']
    racedict[row['FullRace']]['Counties'][row['CountyName']][row['FullName']] = row['CanVotes']
    racedict[row['FullRace']]['Votes'] += row['CanVotes']


paperdict = {}
papergroupdict = OrderedDict()
for paper in papers:
    paperdict[paper] = []
    for county in reportingdict:
        if county in papers[paper]:
            for fullrace in reportingdict[county]:
                if fullrace not in paperdict[paper]:
                    paperdict[paper].append(fullrace)
# Now we should have all the races, but the order is scrambled because there are multiple counties involved.
for paper in paperdict:   # HEY!
    fml = []
    papergroupdict[paper] = OrderedDict()
    for racenamegroup in racenamegroups:
        for racename in racenamegroups[racenamegroup]: # Not a dictionary.
            if racename in paperdict[paper]:
                if racenamegroup not in papergroupdict[paper]:
                    papergroupdict[paper][racenamegroup] = []
                if racename not in fml:
                    papergroupdict[paper][racenamegroup].append(racename)
                    fml.append(racename)
    paperdict[paper] = fml


@app.route('/<paper>/main.html')
def maintemplate(paper):
    print("Trying to generate for " + paper)
    template = 'core.html'
    global paperdict
    global racedict
    global papergroupdict
    global reportingdict
    groupdict = papergroupdict[paper]
    return render_template(template,
                           DetailsWanted=False,
                           groupdict=groupdict,
                           papergroupdict=papergroupdict,
                           racedict=racedict,
                           paperdict=paperdict,
                           paper=paper,
                           reportingdict=reportingdict,
                           timestamp=get_timestamp())

@freezer.register_generator
def getpapernames():
    global paperdict
    for paper in paperdict:
        yield "/" + paper + "/main.html"


# In[18]:

# @app.route('/')
# def bigpicture():
    # print("Trying to generate big-picture template")
    # global paperdict
    # template = "bigpicture.html"
    # return render_template(template,
                           # paperdict=paperdict,
                           # timestamp=get_timestamp())

# @app.route('/<paper>/')
# def smallpicture(paper):
    # print("Trying to generate small-picture template for " + paper)
    # template = 'smallpicture.html'
    # global paperdict
    # global racedict
    # global papergroupdict
    # global reportingdict
    # groupdict = papergroupdict[paper]
    # return render_template(template,
                           # groupdict=groupdict,
                           # papergroupdict=papergroupdict,
                           # racedict=racedict,
                           # paperdict=paperdict,
                           # paper=paper,
                           # reportingdict=reportingdict,
                           # timestamp=get_timestamp())


if __name__ == '__main__':
    # Fire up the Flask test server
    print("Now we're ready to actually start creating the pages.")
    if (len(sys.argv) > 1) and (sys.argv[1] == "build" or sys.argv[1] == "fml"):
        # app.config.update(FREEZER_BASE_URL=buildurl, FREEZER_RELATIVE_URLS=True, FREEZER_DESTINATION="..\homicides-frozen")  # freezer_base_url  kills Python 3.6 for some reason
        app.config.update(FREEZER_RELATIVE_URLS=True, FREEZER_DESTINATION="./built")
        try:
            freezer.freeze()
        except WindowsError:
            print("\tGot that standard Windows error about deleting Git stuff. Life goes on.")
        print("\tAttempting to run post-processing script.")
#         p = Popen(homedir + '/' + "postbake.sh", cwd=homedir)
        p = Popen(homedir + '/' + "postbake.sh", cwd=homedir)
        stdout, stderr = p.communicate()
        print("\tProcessing should be complete.")
    else:
        # from werkzeug.serving import run_simple
        app.config.update(FREEZER_BASE_URL="/", FREEZER_RELATIVE_URLS=True)
        # app.jinja_env.trim_blocks = True
        # app.jinja_env.lstrip_blocks = True

        app.run(debug=True, use_reloader=True, host="0.0.0.0")
        # run_simple('localhost', 5000, app)
