This is an elections results management, editing, parsing, web publishing and print publishing solution based around the *Elex-CSV* pseudo-standard.

In theory, you could go live in minutes by using the [Elex](https://github.com/newsdev/elex) package from the New York Times and National Public Radio, using results from the Associated Press.

This was built to allow people to publish election results in near-real time, using AP results, local scrapers or a combination of the two. [Florida-election-results](https://github.com/PalmBeachPost/florida-election-results) is one example of this, pulling in results from a state-level scraper and several county-level scrapers.

Any code that works or reads well should be credited to [Caitlin Ostroff](https://github.com/ceostroff). Any code that fails or is profane should be blamed on [Mike Stucka](https://github.com/stucka).

Friend of the project [Acton Gorton](https://github.com/actongorton) suggested we should use an alternative data model, known as [NIST SP 1500-100](https://www.nist.gov/itl/voting/interoperability/election-results-reporting-cdf). Instead, we're using Elex-CSV for the data. However, the code is built squarely against the [XKCD 2054 standard](https://xkcd.com/2054/).

Installation: Clone repo. Use Python 3. Run *pip install -r requirements.txt* Start editing the configuration file.

The files:
<li>configuration.py -- Documentation on settings, particularly filenames and reportingunitids (such as county names and FIPS codes).
<li>onescripttorunthemall.py -- It is, well, one script to run them all. This is a script drafted for the November 2018 general election to be used by The Palm Beach Post. No one else would want this particular file, but it could be a good starting point. Note that you want to run the scrapers in parallel, as this does.
<li>composite_csvs.py -- Takes all the CSVs that sit in a directory specified in configuration.py, does the most basic check to see if they fit Elex-CSV format, and composites them into a file specified in the configuration.py. Our naming convention: 20-{state}.csv and 70-{county}.csv. The files are composited in alphabetical order, so this should put the higher-ticketed items earlier in the results.
<li>OPTIONAL: middlewarepre.py -- Takes the composited CSV and generates another CSV with each race name, candidate name, incumbency status, party and some other stuff that can be dropped into Google Sheets for editing. You can change the orders of races and candidates in the Google Sheet and have it be reflected in the final output (albeit, it will still group by the first instance of "officename").
<li>Google Sheets: If nothing else, you'll want to drop lots of races. If you've got state-level reports on the U.S. senate election, you'll want to drop your county-level reporting of that race. A sample: https://docs.google.com/spreadsheets/d/1X8gn-hp9qCNYNJuzCEi4E6d-kT9XvXmIWiwMdN7lA00/edit?usp=sharing
<li>middlewarepost.py -- Take your composited CSV and alter it based on your Google Sheet output. Flag races you haven't seen before (but add 'em anyway to the new results file). Fix in which races and candidates should appear.
<li>app.py -- a Python Flask app that generates HTML and text files for your races. To actually publish, run *python app.py fml*
<li>paperdict.pickle, racedict.pickle, paperdict.pickle -- Optional Python files generated from *app.py* that can be used to do further processing in external tools, such as building for a frontend using JSON.   
<li>templates directory -- where Flask gets its stuff. Mad-Libs in the Jinja2 format.
<li>static directory -- where files you want to include traditionally go; things like CSS, logos, dynamic iframe scripts.
<li>built directory -- where Flask puts its stuff.
<li>postbake.py -- Post-processing, which for us is just copying to the correct web folder defined in configuration.py.
  
### Alternatives and background

Politico is trying to do much more than we're looking for, and brings a good deal of complexity. McCElections is no longer maintained and relies on some specific versions of older technologies, which would reasonably require updating. We didn't have the time. The MinnPost project looks good, but isn't working with the AP data we can reasonably expect would be a starting point for most news organizations.

This rig ran successfully for 11 papers in November, and for two races for one paper in March, and in April for another paper. It's fast. It's easy. There's a lot that should work out of the box, and a lot that can be customized. It's fast; three scrapers and full web publishing for 11 papers took something like six seconds to generate. (Adding in the detailed races option, implemented later, would slow it down some but probably not unreasonably so.)
