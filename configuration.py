# Do you want detailed results by county or other subunits to be generated?
WantDetailed = False

# Do you want the number of precincts reporting to show in the print report?
WantPrintPrecincts = False

# Path to web server folder, for processing by postbake.py
webpath = "/var/www/html/elex20190521"

# Google Sheets ID for processed "preclean" file. MUST BE SET BE SHARED WITH ANYONE WHO HAS THE LINK.
# cleaningsheet = "1HSdmS56RdVjHv_J1Q3pHyWllHsMYDaOMDDW8fk_CnRc"
cleaningsheet = "1p-NGV5SeYg0D5mNXDLZfHo6WOr2j6cf7dTv0bNUbof4"
cleaningsheet = "1-5FsRcCW5Xrnu7qZntmW5cMUrNvx3h60IgXPIe3MM_w"
# For papers, you're looking for the reportingunitids to drive the show.
papers = {
    "beaver": ["All"]
    # "palmbeachpost": ["Palm Beach", "12099", "Martin", "12085", "St. Lucie", "12111"],
    # "jacksonville": ["Duval", "12031", "Clay", "12019", "St. Johns", "12109", "Nassau", "12089", "Baker", "12003"],
    # "ocala": ["Alachua", "12001", "Marion", "12083", "Levy", "12075", "Bradford", "12007", "Putnam", "12107", "Citrus", "12017"],
#     "apalachiola": ["Franklin", "12037"]
# ,
    # "nwf": ["Santa Rosa", "12113", "Okaloosa", "12091", "Walton", "12131"],
    # "staugustine": ["St. Johns", "12109"],
    # "daytonabeach": ["Volusia", "12127", "Flagler", "12035"],
    # "lakeland": ["Polk", "12105"],
    # "sarasota": ["Sarasota", "12115", "Manatee", "12081"],
    # "miami": ["Broward", "12011", "Miami-Dade", "12086", "Monroe", "12087"],
    # "bradenton": ["Manatee", "12081"]    
}

# Location of Elex-CSV-formatted scraper output.
datadir = "./rawscrapings/"

# Location of Elex-CSV-formatted scraper output combined
resultscomposite = "./resultscomposite.csv"

# Location of file that can be dropped into Google Sheets for editing of race details. Want to declare a winner?
cleaningpre = "./resultspreclean.csv"

# Name to temporary storage file of exported Google Sheet CSV from above
cleaningtemp = "./resultscleaningtemp.csv"

# path to save timestamped versions of downloaded data. Sample: "./snapshots/"
snapshotsdir = "./snapshots/"

# Processed file with correct dropped races, declared races, dropped candidates, all that.
cleaningdone = "./resultscleaned.csv"
