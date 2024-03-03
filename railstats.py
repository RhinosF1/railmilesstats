import json
import sys
counts = dict()
counts['origins'] = {}
counts['dests'] = {}
counts['station_visits'] = {}
counts['arrival_status'] = {}
counts['dept_status'] = {}
counts['delaymins'] = 0
counts['duration'] = 0
counts['distance'] = 0.0
counts['operator'] = {}
counts['identity'] = {}
counts['reason'] = {}
counts['traction'] = {}
counts['class'] = {}
counts['arrival_status_by_operator'] = {}
counts['delaymins_by_operator'] = {}
counts['duration_by_operator'] = {}
counts['duration/delay_by_operator'] = {}
counts['percent_delayed_by_operator'] = {}
with open(str(sys.argv[1])) as f:
    data = json.loads(f.read())
    for row in data['journeys']:
        if row['origin'] in counts['origins']:
            counts['origins'][row['origin']] += 1
        else:
            counts['origins'][row['origin']] = 1

        if row['destination'] in counts['dests'].keys():
            counts['dests'][row['destination']] += 1
        else:
            counts['dests'][row['destination']] = 1
        
        if row['origin'] in counts['station_visits']:
            counts['station_visits'][row['origin']] += 1
        else:
            counts['station_visits'][row['origin']] = 1

        if row['destination'] in counts['station_visits']:
            counts['station_visits'][row['destination']] += 1
        else:
            counts['station_visits'][row['destination']] = 1  

        if row['act_arrival_status'] == "":
            row['act_arrival_status'] = "RT"
        if row['act_arrival_status'] in counts['arrival_status']:
            counts['arrival_status'][row['act_arrival_status']] += 1
        else:
            counts['arrival_status'][row['act_arrival_status']] = 1
        if row['operator']['code'] not in counts['arrival_status_by_operator'].keys():
            counts['arrival_status_by_operator'][row['operator']['code']] = {}
        if row['act_arrival_status'] in counts['arrival_status_by_operator'][row['operator']['code']]:
            counts['arrival_status_by_operator'][row['operator']['code']][row['act_arrival_status']] += 1
        else:
            counts['arrival_status_by_operator'][row['operator']['code']][row['act_arrival_status']] = 1

        if row['act_departure_status'] == '':
            row['act_departure_status'] = 'RT'
        if row['act_departure_status'] in counts['dept_status']:
            counts['dept_status'][row['act_departure_status']] += 1
        else:
            counts['dept_status'][row['act_departure_status']] = 1

        if row['act_delay'] and not row['act_delay'] < 0:
            counts['delaymins'] += row['act_delay']
            if row['operator']['code'] not in counts['delaymins_by_operator'].keys():
                counts['delaymins_by_operator'][row['operator']['code']] = 0
            counts['delaymins_by_operator'][row['operator']['code']] += row['act_delay']
        if row['duration']:
            counts['duration'] += row['duration']
            if row['operator']['code'] not in counts['duration_by_operator'].keys():
                counts['duration_by_operator'][row['operator']['code']] = 0
            counts['duration_by_operator'][row['operator']['code']] += row['duration']
        if row['distance']['value']:
            counts['distance'] += float(row['distance']['value'])

        if row['operator']['code'] is None:
            row['operator']['code'] = 'Unknown'
        if row['operator']['code'] in counts['operator']:
            counts['operator'][row['operator']['code']] += 1
        else:
            counts['operator'][row['operator']['code']] = 1

        if row['identity'] is None:
            row['identity'] = 'Unknown'
        if row['identity'] in counts['identity']:
            counts['identity'][row['identity']] += 1
        else:
            counts['identity'][row['identity']] = 1
        
        if row['reason'] is None:
            row['reason'] = 'Unknown'
        if row['reason'] in counts['reason']:
            counts['reason'][row['reason']] += 1
        else:
            counts['reason'][row['reason']] = 1
        if len(row['traction']) == 0:
            row['traction'] = ['Unknown']
        for traction in row['traction']:
            trclass = traction[:3]
            if traction in counts['traction']:
                counts['traction'][traction] += 1
            else:
                counts['traction'][traction] = 1
            if trclass in counts['class']:
                counts['class'][trclass] += 1
            else:
                counts['class'][trclass] = 1
    for operator in counts['operator']:
        counts['percent_delayed_by_operator'][operator] = 0.0
        if 'late' in counts['arrival_status_by_operator'][operator]:
            counts['percent_delayed_by_operator'][operator] = counts['arrival_status_by_operator'][operator]['late'] / counts['operator'][operator]

    counts['duration/delay'] = counts['duration'] / counts['delaymins']
    counts['delay/distance'] = counts['delaymins'] / counts['distance']
    counts['speed'] = (int(counts['distance']) / counts['duration'])*60
    counts['journeys'] = len(data['journeys'])
    counts['delay/journey'] = counts['delaymins'] / counts['journeys']
    for operator in counts['duration_by_operator']:
        if operator in counts['delaymins_by_operator']:
            if (counts['delaymins_by_operator'][operator] > 0):
                counts['duration/delay_by_operator'][operator] = counts['duration_by_operator'][operator] / counts['delaymins_by_operator'][operator]
        else:
            counts['duration/delay_by_operator'][operator] = counts['duration_by_operator'][operator]

    for item in counts:
        if item not in ['arrival_status_by_operator'] and isinstance(counts[item], dict):
                temp = counts[item]
                sorted_temp = sorted(temp.items(), key=lambda x : x[1])
                sorted_temp = dict(sorted_temp)
                counts[item] = sorted_temp
late_operators = []
for operator in counts['arrival_status_by_operator']:
    if 'late' in counts['arrival_status_by_operator'][operator]:
        late_operators.append(operator)
worst_operator_by_delayed_journeys = late_operators[0]
for operator in late_operators:
    if counts['arrival_status_by_operator'][operator]['late'] > counts['arrival_status_by_operator'][worst_operator_by_delayed_journeys]['late']:
        worst_operator_by_delayed_journeys = operator


late_operators = []
for operator in counts['delaymins_by_operator']:
    if counts['delaymins_by_operator'][operator] > 2:
        late_operators.append(operator)
worst_operator_by_delaymins = late_operators[0]
for operator in late_operators:
    if counts['delaymins_by_operator'][operator] > counts['delaymins_by_operator'][worst_operator_by_delaymins]:
        worst_operator_by_delaymins = operator

print('DEBUG OUTPUT')
print(json.dumps(counts, indent=2))
print('Pretty Output')
print(f'Between {sys.argv[2]} and {sys.argv[3]}, I have taken {counts["journeys"]} rail journeys spanning {int(counts["distance"])} miles taking {counts["duration"]} minutes.')
print(f'That makes for an average speed of {int(counts["speed"])}mph and an average journey length of {int(counts["distance"]/counts["journeys"])} miles so {int((counts["duration"])/(counts["journeys"]))} minutes per journey.')
print(f'This involved arriving or departing from {len(counts["station_visits"])} different stations with the most popular being {list(counts["station_visits"])[-1]}.')
print(f'All of the stations I visted were:')
print(*list(counts['station_visits']), sep=', ')
print(f'The most popular operator was {list(counts["operator"])[-1]} of the {len(counts["operator"])} I used and most popular traction {list(counts["traction"])[-1]} of {len(counts["traction"])} units I\'ve been on.')
print(f'I have seen the most of class {list(counts["class"])[-1]} trains with {counts["class"][list(counts["class"])[-1]]} occurences of them.')
print(f'We managed to arrive early on {counts["arrival_status"]["early"]} occassions, on time {counts["arrival_status"]["RT"]} times but were late {counts["arrival_status"]["late"]} times.')
print(f'We make for an average of {counts["delay/distance"]} delay minutes per mile or {int(counts["delay/journey"])} minutes per journey.')
print(f'The most used headcode was {list(counts["identity"])[-1]}.')
print(f'{worst_operator_by_delayed_journeys} scores the most delayed journeys with {counts["arrival_status_by_operator"][worst_operator_by_delayed_journeys]["late"]} journeys delayed.')
print(f'but compared to number of journeys, the most likely operator for a delay is {list(counts["percent_delayed_by_operator"])[-1]} with {int((counts["percent_delayed_by_operator"][list(counts["percent_delayed_by_operator"])[-1]])*100)}% delayed.')
print(f'{worst_operator_by_delaymins} scores the most delay minutes with {counts["delaymins_by_operator"][worst_operator_by_delaymins]} minutes delay.')
print(f'but compared to duration, the most likely operator for a delay is {list(counts["duration/delay_by_operator"])[0]} with {int(counts["duration/delay_by_operator"][list(counts["duration/delay_by_operator"])[0]])} delay minutes per minute travel.')
print(f'Our operators with 0% delays are:')
no_delay_ops = []
for operator in counts['percent_delayed_by_operator']:
    if counts['percent_delayed_by_operator'][operator] == 0.0:
        no_delay_ops.append(operator)
print(*list(no_delay_ops), sep=', ')
print(f'The most to-time operator by delays per minute travelled is {list(counts["duration/delay_by_operator"])[-1]} with {int(counts["duration/delay_by_operator"][list(counts["duration/delay_by_operator"])[-1]])} minutes of travel needed per minute of delay.')
print(f'My most popular reason for travel is {list(counts["reason"])[-1]} with {counts["reason"][list(counts["reason"])[-1]]} journeys')
