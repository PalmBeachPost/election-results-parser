"""
To-do list:
-- Implement to-do list
"""
from flask import Flask, render_template, redirect, url_for, request   # External dependency
from flask_frozen import Freezer
from slugify import slugify         # awesome-slugify, from requirements
import dateparser

import configuration    # configuration.py, with user-defined variables.

import csv
import time
import datetime
from collections import OrderedDict
import pprint
import os
import sys
from subprocess import Popen
import pickle
from decimal import *

datadir = configuration.datadir
resultscomposite = configuration.resultscomposite
cleaningdone = configuration.cleaningdone
papers = configuration.papers
getcontext().prec = 10      # Precision
pp = pprint.PrettyPrinter(indent=4)

app = Flask(__name__)
freezer = Freezer(app)


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
    return(slugify(text))


@app.template_filter('percentageifier')
def percentageifier(text):
    return(str((Decimal(100) * Decimal(text)).quantize(Decimal("1.0"))))
    # HEY! Change precision   return(str((Decimal(100) * Decimal(text)).quantize(Decimal("1.000"))))


@app.template_filter('hunnertifier')
def hunnertifier(text):
    return(str(int((Decimal(100) * Decimal(text)).quantize(Decimal("1")))))


@app.template_filter('timestampifier')
def timestampifier(text):
    dateobject = dateparser.parse(text)
    thingy = datetime.datetime.strftime(dateobject, "%I:%M %p")     # 05:23 PM
    if thingy[0] == "0":
        thingy = thingy[1:]     # Strip off 0 prefix for hours less than 10
    thingy = thingy.replace(" AM", " a.m.").replace(" PM", " p.m.")
    return(thingy)


@app.template_filter('partyfier')
def partyfier(party):
    prefix = " ("
    suffix = ")"
    if len(party) == 0:
        thingy = ""
    elif "gop" in party.lower() or "rep" in party.lower():
        thingy = prefix + "R" + suffix
    elif "dem" in party.lower():
        thingy = prefix + "D" + suffix
    elif "libertarian" in party.lower():
        thingy = prefix + "LIB" + suffix
    elif "reform" in party.lower():
        thingy = prefix + "Reform" + suffix
    elif "green" in party.lower():
        thingy = prefix + "Green" + suffix
    elif "no party" in party.lower() or "npa" in party.lower():
        thingy = ""
    else:
        thingy = ""
    return(thingy)


@app.template_filter('printpartyfier')
def printpartyfier(party):
    prefix = " ("
    suffix = ")"
    if len(party) == 0:
        thingy = ""
    elif "gop" in party.lower() or "rep" in party.lower():
        thingy = prefix + "R" + suffix
    elif "dem" in party.lower():
        thingy = prefix + "D" + suffix   # HEY! This should maybe go back next time
    # elif "libertarian" in party.lower():
        # thingy = prefix + "LIB" + suffix
    # elif "reform" in party.lower():
        # thingy = prefix + "Reform" + suffix
    # elif "green" in party.lower():
        # thingy = prefix + "Green" + suffix
    elif "no party" in party.lower() or "npa" in party.lower():
        thingy = ""
    else:
        thingy = ""
    return(thingy)


@app.template_filter('winner')
def winner(text):
    if "y" in text.lower() or "true" in text.lower():
        return("x-")
    else:
        return("")


@app.template_filter('runoff')
def runoff(text):
    if "y" in text.lower() or "true" in text.lower():
        return("r-")
    else:
        return("")


@app.template_filter('incumbencyer')
def incumnbencyer(incumbent):
    if "y" in incumbent.lower() or "true" in incumbent.lower():
        thingy = " *"
    else:
        thingy = ""
    return(thingy)


@app.template_filter('printincumbencyer')
def printincumnbencyer(incumbent):
    if "y" in incumbent.lower() or "true" in incumbent.lower():
        thingy = "*"
    else:
        thingy = ""
    return(thingy)


def cleanrow(row):
    for item in ["electtotal", "precinctsreporting", "precinctstotal", "votecount"]:
        if row[item] == '':
            print(item)
            print(row)
            row[item] = 0
        else:
            row[item] = int(row[item])
    # precinctsreportingpct
    # votepct
    return(row)


# with open(resultscomposite, "r") as f:    # Import the data and do some basic cleaning
with open(cleaningdone, "r") as f:    # Import the data and do some basic cleaning
    masterlist = []
    for row in csv.DictReader(f):
        masterlist.append(cleanrow(row))

reportingdict = OrderedDict()   # Holds reporting unit ID?
racedict = OrderedDict()

for row in masterlist:
    # Begin basic setup
    # OK, before reportingdict held countynames. The values were the names of races, which we wanted to be unique.
    # Now we want reportingdict to hold reportingunitid (county IDs, not names).
    # And instead of names of races we want the raceid, which must be unique.

    if row['reportingunitid'] not in reportingdict:
        reportingdict[row['reportingunitid']] = []
    if row['raceid'] not in reportingdict[row['reportingunitid']]:
        reportingdict[row['reportingunitid']].append(row['raceid'])

# OK, so we were going by racedict holding unique race names. We can't do that any more.
# So let's have racedict hold raceids , and the racename / officename will be a value.
    if row['raceid'] not in racedict:
        racedict[row['raceid']] = OrderedDict()
        for item in ["electtotal", "precinctsreporting", "precinctsreportingpct", "precinctstotal"]:
            racedict[row['raceid']][item] = 0
        for item in ['officeid', 'officename', 'racetypeid', 'seatname', 'seatnum', 'lastupdated']:
            racedict[row['raceid']][item] = row[item]

# Now, we want everything keyed to the reportingunitid instead of the county name, right?
        racedict[row['raceid']]['reportingunitid'] = OrderedDict()
        racedict[row['raceid']]['candidateid'] = OrderedDict()
    if row['candidateid'] not in racedict[row['raceid']]['candidateid']:
        racedict[row['raceid']]['candidateid'][row['candidateid']] = {}
        racedict[row['raceid']]['candidateid'][row['candidateid']]['votecount'] = 0
        for item in ['first', 'incumbent', 'last', 'party', 'runoff', 'uncontested', 'winner']:
            racedict[row['raceid']]['candidateid'][row['candidateid']][item] = row[item]
    if row['reportingunitid'] not in racedict[row['raceid']]['reportingunitid']:
        racedict[row['raceid']]['reportingunitid'][row['reportingunitid']] = OrderedDict()
        racedict[row['raceid']]['reportingunitid'][row['reportingunitid']]['candidateid'] = OrderedDict()
        racedict[row['raceid']]['reportingunitid'][row['reportingunitid']]['reportingunitname'] = row['reportingunitname']
        racedict[row['raceid']]['reportingunitid'][row['reportingunitid']]['precinctsreporting'] = row['precinctsreporting']
        racedict[row['raceid']]['reportingunitid'][row['reportingunitid']]['precinctstotal'] = row['precinctstotal']
        racedict[row['raceid']]['reportingunitid'][row['reportingunitid']]['precinctsreportingpct'] = row['precinctsreportingpct']
        racedict[row['raceid']]['reportingunitid'][row['reportingunitid']]['electtotal'] = row['electtotal']
        racedict[row['raceid']]['precinctstotal'] += row['precinctstotal']
        racedict[row['raceid']]['precinctsreporting'] += row['precinctsreporting']
    racedict[row['raceid']]['reportingunitid'][row['reportingunitid']]['electtotal'] = row['electtotal']
    racedict[row['raceid']]['candidateid'][row['candidateid']]['votecount'] += row['votecount']
    racedict[row['raceid']]['reportingunitid'][row['reportingunitid']][row['candidateid']] = row['votecount']
    racedict[row['raceid']]['electtotal'] += row['votecount']

for race in racedict:
    if racedict[race]['precinctstotal'] == 0:
        racedict[race]['precinctsreportingpct'] = 0
    else:
        racedict[race]['precinctsreportingpct'] = (
            Decimal(racedict[race]['precinctsreporting']) /
            Decimal(racedict[race]['precinctstotal'])
            )
    for candidateid in racedict[race]['candidateid']:
        if racedict[race]['electtotal'] == 0:
            racedict[race]['candidateid'][candidateid]['votepct'] = 0
        else:
            racedict[race]['candidateid'][candidateid]['votepct'] = (
                Decimal(racedict[race]['candidateid'][candidateid]['votecount']) /
                Decimal(racedict[race]['electtotal'])
                )

paperdict = {}
papergroupdict = OrderedDict()
for paper in papers:
    paperdict[paper] = []
    for reportingunitid in reportingdict:
        if reportingunitid in papers[paper]:
            for raceid in reportingdict[reportingunitid]:
                if raceid not in paperdict[paper]:
                    paperdict[paper].append(raceid)

# Now we should have all the races, but the order is scrambled because there are multiple counties involved.
for paper in paperdict:
    fml = []
    for raceid in racedict:
        if raceid in paperdict[paper]:
            if raceid not in fml:
                fml.append(raceid)
    paperdict[paper] = fml

# Now we have paperdict holding a list of papers. And each paper includes the raceid, which is great.
# But let's take this just a step farther -- we have some races with common names, e.g. "U.S. Congress"
# So let's take a look at the officename and build against that, such that:
# masterdict -> papername -> group of officenames -> individual races -> everything from racedict

masterdict = OrderedDict()
for paper in paperdict:
    masterdict[paper] = OrderedDict()
    for raceid in paperdict[paper]:
        groupname = racedict[raceid]['officename']
        if groupname not in masterdict[paper]:
            masterdict[paper][groupname] = OrderedDict()
        masterdict[paper][groupname][raceid] = racedict[raceid]

with open("paperdict.pickle", "wb") as f:
    pickle.dump(paperdict, f)
with open("masterlist.pickle", "wb") as f:
    pickle.dump(masterlist, f)
with open("racedict.pickle", "wb") as f:
    pickle.dump(racedict, f)


@app.route('/<paper>/main.html')
def maintemplate(paper):
    print("Trying to generate for " + paper)
    template = 'main.html'
    global masterdict
    global reportingdict
    return render_template(
        template,
        DetailsWanted=False,
        paper=masterdict[paper],
        papername=paper,
        reportingdict=reportingdict
        )


@app.route('/<paper>/print.txt')
def printtemplate(paper):
    print("Trying to generate for " + paper)
    template = 'print.txt'
    global masterdict
    hardcodingisbad = ["260540", "260550", "260830", "260840", "551919"]
    printpaperdict = OrderedDict()
    for groupname in masterdict[paper]:
        printpaperdict[groupname] = OrderedDict()
        for raceid in masterdict[paper][groupname]:
            if raceid not in hardcodingisbad:
                printpaperdict[groupname][raceid] = masterdict[paper][groupname][raceid]
            else:
                print("Dropping race " + raceid)
    global reportingdict
    return render_template(
        template,
        DetailsWanted=False,
        paper=printpaperdict,
        papername=paper,
        reportingdict=reportingdict
        )


@app.route('/<paper>/racegroups/<slugifiedgroupname>.html')
def racegroup(paper, slugifiedgroupname):
    template = 'racegroup.html'
    global masterdict
    global racedict
    global paperdict
    oneracedict = OrderedDict()
    for raceid in paperdict[paper]:
        groupname = racedict[raceid]['officename']
        localslug = slugify(groupname)
        if localslug == slugifiedgroupname:
            localdict = OrderedDict()
            localdict[groupname] = masterdict[paper][groupname]
            # print(localdict)
            return render_template(
                template,
                paper=localdict,
                papername=paper
                )


@app.route('/<paper>/races/<slugifiedracename>.html')
def onerace(paper, slugifiedracename):
    template = 'race.html'
    global masterdict
    global racedict
    global paperdict
    oneracedict = OrderedDict()
    for raceid in paperdict[paper]:
        groupname = racedict[raceid]['officename']
        seatname = racedict[raceid]['seatname']
        seatnum = racedict[raceid]['seatnum']
        racename = groupname
        if len(seatname + seatnum) > 0:   # if we have those details:
            if len(seatname) > 0:   # prefer seatname to seatnum
                racename += " " + seatname
            else:
                racename += " " + seatnum
        localslug = slugify(racename)
        if localslug == slugifiedracename:
            oneracedict = racedict[raceid]
            return render_template(
                template,
                oneracedict=oneracedict,
                papername=paper,
                racename=racename
                )


@freezer.register_generator
def getpapernames():
    global paperdict
    global racedict
    for paper in paperdict:
        yield "/" + paper + "/main.html"
        yield "/" + paper + "/print.txt"
        groupnames = []
        racenames = []
        for raceid in paperdict[paper]:
            groupname = racedict[raceid]['officename']
            seatname = racedict[raceid]['seatname']
            seatnum = racedict[raceid]['seatnum']
            racename = groupname
            if len(seatname + seatnum) > 0:   # if we have those details:
                if len(seatname) > 0:   # prefer seatname to seatnum
                    racename += " " + seatname
                else:
                    racename += " " + seatnum
            if groupname not in groupnames:
                groupnames.append(groupname)
                slugifiedgroupname = slugify(groupname)
                yield "/" + paper + "/racegroups/" + slugifiedgroupname + ".html"
            if racename not in racenames:
                racenames.append(racename)
                slugifiedracename = slugify(racename)
                yield "/" + paper + "/races/" + slugifiedracename + ".html"


if __name__ == '__main__':
    # Fire up the Flask test server
    print("Now we're ready to actually start creating the pages.")
    if (len(sys.argv) > 1) and (sys.argv[1] == "build" or sys.argv[1] == "fml"):
        app.config.update(FREEZER_RELATIVE_URLS=True, FREEZER_DESTINATION="./built")
        try:
            freezer.freeze()
        except WindowsError:
            print("\tGot that standard Windows error about deleting Git stuff. Life goes on.")
        print("\tAttempting to run post-processing script.")
        os.system("python postbake.py")
        print("All done!")
        print("\tProcessing should be complete.")
    else:
        app.config.update(FREEZER_BASE_URL="/", FREEZER_RELATIVE_URLS=True)
        app.run(debug=True, use_reloader=True, host="0.0.0.0")
        # run_simple('localhost', 5000, app)
