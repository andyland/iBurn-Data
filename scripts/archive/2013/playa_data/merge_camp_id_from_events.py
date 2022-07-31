import Levenshtein
import json
from string_util import cleanString
'''
    This script merges camp ids into the data from 
    ./data/playaevents-camps-2013.json
    OR ./results/camp_data_and_locations.json
    using playaevents-events-2013
    (The Playa Events API Events feed)
'''

# Threshold under which to discard partial string matches
MATCH_THRESHOLD = .7

camp_file = open('./results/camp_data_and_locations.json')
events_file = open('./data/playaevents-events-2013.json')

camp_json = json.loads(camp_file.read())
events_json = json.loads(events_file.read())

# Some entries in event_data are null, remove them before writing final json
null_camp_indexes = []

# camps without a match, for manual inspection
unmatched_camps = []

matched_camps = []

# match name fields between entries in two files
for index, camp in enumerate(camp_json):
    max_match = 0
    max_match_event = ''
    if camp != None and 'name' in camp:
        for event in events_json:
            if 'hosted_by_camp' in event:
                match = Levenshtein.ratio(cleanString(camp['name']), cleanString(event['hosted_by_camp']['name']))
                if match > max_match:
                    max_match = match
                    max_match_event = event
        #print "Best match for " + event['name'] + " : " + max_match_camp['name'] + " (confidence: " + str(max_match) + ")"
        if max_match > MATCH_THRESHOLD:
            # Match found
            camp['id'] = max_match_event['hosted_by_camp']['id']
            matched_camps.append(camp)
        else:
            unmatched_camps.append(camp)
    elif not 'name' in camp:
        null_camp_indexes.append(index)

# To remove null entries from list, we must move in reverse
# to preserve list order as we remove
null_camp_indexes.reverse()
for index in null_camp_indexes:
    camp_json.pop(index)

unmatched_camps_file = open('./results/unmatched_camps_id.json', 'w')
unmatched_camps_file.write(json.dumps(unmatched_camps, sort_keys=True, indent=4))

result_file = open('./results/camp_data_and_locations_ids.json', 'w')
result_file.write(json.dumps(camp_json, sort_keys=True, indent=4))

if len(unmatched_camps) > 0:
    print "Matches not found for " + str(len(unmatched_camps)) + " camps"

print "Matched: "+str(len(matched_camps))
