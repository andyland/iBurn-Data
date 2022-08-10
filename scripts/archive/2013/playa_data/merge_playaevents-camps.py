'''
    This script merges camp locations from camp-locations-2013.json
    into camp entries from playaevents-camps-2013.json
    (The Playa Events API Camp feed)
    AND camps-2012.json (optional)
    (The result of scraper.py in the iBurn-2011 iOS repo)
'''

import Levenshtein
import json
from string_util import cleanString, convert_html_entities
import codecs

# Threshold under which to discard partial string matches
MATCH_THRESHOLD = .7

location_file = open('./data/camp-locations-2013.json')
playa_file = open('./data/playaevents-camps-2013.json')
scraper_file = open('./data/camps-2013.json')
# Comment out the above line to disable the scraper.py datasource

location_json = json.loads(location_file.read())
playa_json = json.loads(playa_file.read())
if scraper_file:
    scraper_json = json.loads(scraper_file.read())

# Some entries in camp_data are null, remove them before writing final json
null_camp_indexes = []

# camps without a match, for manual inspection
unmatched_camps = []

matched_camps = []

# First, merge camps-2012.json data into playaevents-camps-2012.json
if scraper_file:
    for scraper_camp in scraper_json:
        max_match = 0
        max_match_playa_camp_index = -1
        if scraper_camp != None:
            for index, playa_camp in enumerate(playa_json):
                if playa_camp != None:
                    match = Levenshtein.ratio(cleanString(playa_camp['name']), cleanString(scraper_camp['name']))
                    if match > max_match:
                        max_match = match
                        max_match_playa_camp_index = index
            matchDict = None
            if max_match > MATCH_THRESHOLD:
                matchDict = playa_json[max_match_playa_camp_index]
            else:
              #print "Best match for " + camp['name'] + " : " + max_match_location['name'] + " (confidence: " + str(max_match) + ")"
              
              matchDict = {}
              matchDict['name'] = scraper_camp['name']
              playa_json.append(matchDict)
                
            if 'description' in scraper_camp:
                matchDict['description'] = scraper_camp['description']
            if 'contact' in scraper_camp:
                matchDict['contact_email'] = scraper_camp['contact']
            if 'hometown' in scraper_camp:
                matchDict['hometown'] = scraper_camp['hometown']
            if 'url' in scraper_camp:
                matchDict['url'] = scraper_camp['url']
            if 'name' in scraper_camp:
                matchDict['alt_name'] = scraper_camp['name']
      
            #print "merged scraper entry: " + str(scraper_camp['name'])


# match name fields between entries in two files
for index, camp in enumerate(playa_json):
    max_match = 0
    max_match_location = ''
    if camp != None:
        for location in location_json:
                match = Levenshtein.ratio(cleanString(location['name']), cleanString(camp['name']))
                if match > max_match:
                    max_match = match
                    max_match_location = location
        if max_match > MATCH_THRESHOLD:
            # Match found
            if 'latitude' in max_match_location and max_match_location['latitude'] != "":
                camp['latitude'] = max_match_location['latitude']
                camp['longitude'] = max_match_location['longitude']
            #camp['location'] = max_match_location['location']
            camp['matched_name'] = max_match_location['name']
            matched_camps.append(camp)
        else:
          print "Best match for " + camp['name'] + " : " + max_match_location['name'] + " (confidence: " + str(max_match) + ")"
          unmatched_camps.append(camp)
          
    else:
        null_camp_indexes.append(index)

# To remove null entries from list, we must move in reverse
# to preserve list order as we remove
null_camp_indexes.reverse()
for index in null_camp_indexes:
    playa_json.pop(index)

unmatched_camps_file = codecs.open('./results/unmatched_camps.json', 'w', "utf-8")
json_content = json.dumps(unmatched_camps, sort_keys=True, indent=4)
json_stripped = json_content.strip(codecs.BOM_UTF8)
json_stripped_cleaned = convert_html_entities(json_stripped)
unmatched_camps_file.write(json_stripped_cleaned)
#unmatched_camps_file.write(convert_html_entities(json.dumps(unmatched_camps, sort_keys=True, indent=4)).strip(codecs.BOM_UTF8))

result_file = codecs.open('./results/camp_data_and_locations.json', 'w', "utf-8")
json_content = json.dumps(playa_json, sort_keys=True, indent=4)
json_stripped = json_content.strip(codecs.BOM_UTF8)
json_stripped_cleaned = convert_html_entities(json_stripped)
result_file.write(json_stripped_cleaned)
#result_file.write(convert_html_entities(json.dumps(playa_json, sort_keys=True, indent=4)).strip(codecs.BOM_UTF8))

if len(unmatched_camps) > 0:
    print "Location not determined for " + str(len(unmatched_camps)) + " camps"

print "Matched camps: "+str(len(matched_camps))
