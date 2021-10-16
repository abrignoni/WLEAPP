#!/usr/bin/env python3
import json
import datetime
import os

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows

def get_betterDiscord(files_found, report_folder, seeker, wrap_text):
    
    for file_found in files_found:
        file_found = str(file_found)
        if not os.path.basename(file_found) == 'MessageLoggerV2Data.config.json': # skip -journal and other files
            continue
    
        with open(file_found, "r") as fp:
            deserialized = json.load(fp)
        
        data_list = []
        for key, value in deserialized['data'].items():
            #print(key)
            if key == "messageRecord":
                for keylin, valuein in value.items():
                    #print(valuein['message'])
                    timestamp = valuein['message']['timestamp']
                    timestamp = datetime.datetime.fromtimestamp(int(timestamp)/1000).strftime('%Y-%m-%d %H:%M:%S.%f')
                    username = valuein['message']['author']['username']
                    content = valuein['message']['content']
                    referencing = valuein['message'].get('referenced_message')
                    aggregator = ' '
                    if referencing:
                        control = 1
                        aggregator = aggregator + ('<table>')
                        while(control):
                            aggregator = aggregator +('<tr>')
                            timestamp_in = referencing.get('timestamp')
                            timestamp_in = datetime.datetime.fromtimestamp(int(timestamp_in)/1000).strftime('%Y-%m-%d %H:%M:%S.%f')
                            username_in = referencing['author'].get('username')
                            content_in = referencing.get('content')
                            referencing = referencing.get('referenced_message')
                            aggregator = aggregator + f'<td>{timestamp_in}</td>'
                            aggregator = aggregator + f'<td>{username_in}</td>'
                            aggregator = aggregator + f'<td>{content_in}</td>'
                            aggregator = aggregator +('</tr>')
                            if referencing:
                                control = 1
                            else:
                                control = 0
                                aggregator = aggregator + ('</table>')
                    data_list.append((timestamp, username, content, aggregator.strip()))
    
    num_entries = len(data_list)
    if num_entries > 0:
        report = ArtifactHtmlReport('Better Discord')
        report.start_artifact_report(report_folder, 'Better Discord')
        report.add_script()
        data_headers = ('Timestamp','Username','Content','Referenced Messages')
        
        report.write_artifact_data_table(data_headers, data_list, file_found,html_no_escape=['Referenced Messages'])
        report.end_artifact_report()
        
        tsvname = f'Better Discord'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = f'Better Discord'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No Better Discord data available')
        
    