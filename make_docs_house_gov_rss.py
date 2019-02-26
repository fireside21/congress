#! /usr/bin/env python

# -*- coding: utf-8 -*-

from json import load, dumps
from dateutil.parser import parse
from codecs import open as copen

# First, run
#   ./run committee_meetings --chamber=house --load_by=100031-115000 --docs=False

with open('data/committee_meetings_house.json') as f:
    json = load(f)

print('ID Range: {} to {}. {} total'.format(
    min(m['house_event_id'] for m in json),
    max(m['house_event_id'] for m in json),
    len(json)
))

by_cmte = {}
for m in json:
    cmte_id = m['committee'][2:]
    if cmte_id in by_cmte:
        by_cmte[cmte_id].append(m)
    else:
        by_cmte[cmte_id] = [m]

print(by_cmte.keys())

item_fmt = u'''
<item>
    <guid>{id}</guid>
    <title>{m[topic]}</title>
    <description>{cmte_name}<br />Meeting Date: {date:%A, %B %-d, %Y %-I:%M %p} {m[room]}</description>
    <pubDate>Fri, 28 Dec 2018 17:39:03 GMT</pubDate>
    <link>{m[url]}</link>
    <enclosure url="http://docs.house.gov/Meetings/{cmte_id}/{cmte_id}{sub_cmte_id}/{date:%Y%m%d}/{id}/{type}-{m[congress]}-{cmte_id}{sub_cmte_id}-{date:%Y%m%d}.xml" type="text/xml" />
</item>
'''

for cmte_id in by_cmte:
    with copen('data/committee/meetings/house/{}.rss'.format(cmte_id), 'w', 'utf8') as f:
        f.write('''<rss version="2.0">
<channel>
<title>U.S. House of Representatives - {} Committee Feed</title>
<link>http://docs.house.gov/committee</link>
<description>Published Committee Meetings</description>
<language>en-US</language>
<pubDate>Tue, 29 Jan 2019 20:03:06 GMT</pubDate>'''.format(cmte_id))
        for meeting in sorted(by_cmte[cmte_id], key=lambda m: m['occurs_at']):
            args = {
                'm': meeting,
                'id': meeting['house_event_id'],
                'cmte_name': meeting['committee_names'][0],
                'cmte_id': cmte_id,
                'sub_cmte_id': meeting['subcommittee'] if meeting['subcommittee'] else '00',
                'type': meeting['house_meeting_type'],
                'date': parse(meeting['occurs_at']),
            }
            f.write(item_fmt.format(**args))
        f.write('</channel>\n</rss>')
