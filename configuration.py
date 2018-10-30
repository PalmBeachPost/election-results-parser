# For papers, you're looking for the reportingunitids to drive the show.
papers = {
    "palmbeachpost": ["Palm Beach", "12099", "Martin", "12085", "St. Lucie", "12111"],
    "jacksonville": ["Duval", "12031", "Clay", "12019", "St. Johns", "12109", "Nassau", "12089", "Baker", "12003"],
    "ocala": ["Alachua", "12001", "Marion", "12083", "Levy", "12075", "Bradford", "12007", "Putnam", "12107", "Citrus", "12017"],
    "apalachiola": ["Franklin", "12037"],
    "nwf": ["Santa Rosa", "12113", "Okaloosa", "12091", "Walton", "12131"],
    "staugustine": ["St. Johns", "12109"],
    "daytonabeach": ["Volusia", "12127", "Flagler", "12035"],
    "lakeland": ["Polk", "12105"],
    "sarasota": ["Sarasota", "12115", "Manatee", "12081"],
    "miami": ["Broward", "12011", "Miami-Dade", "12086", "Monroe", "12087"],
    "bradenton": ["Manatee", "12081"]    
}

# Location of Elex-CSV-formatted scraper output.
datadir = "./rawscrapings/"

# Location of Elex-CSV-formatted scraper output combined
resultscomposite = "./resultscomposite.csv"

# Location of file that can be dropped into Google Sheets for editing of race details. Want to declare a winner?
cleaningpre = "./resultspreclean.csv"

# Google Sheets ID to processed "preclean" file
cleaningsheet = ""

# Processed file with correct dropped races, declared races, dropped candidates, all that.
cleaningdone = "./resultstobeprocessed.csv"