#!/usr/bin/env python3
import json
import datetime
import os

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows

def get_pfirewall(files_found, report_folder, seeker, wrap_text):
    
    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('pfirewall.log'):
            continue # Skip all other files
    
        data_list = []
        
        with open(file_found, 'r') as file:
            lines = file.readlines()
            
        for iteration, x in enumerate(lines):
            if 'Version' in x:
                firewallversion = x
            if iteration > 4:
                fields = x.split(' ')
                #print(fields)
                date = fields[0].strip()
                time = fields[1]
                timestamp = f'{date} {time}'
                action = fields[2]
                protocol = fields[3]
                sourceip = fields[4]
                destip = fields[5]
                sourceport = fields[6]
                destport = fields[7]
                size = fields[8]
                tcpflags = fields[9] 
                tcpsyn = fields[10]
                tcpack = fields[11]
                tcpwin = fields[12]
                icmptype = fields[13]
                icmpcode = fields[14]
                info = fields[15]
                path = fields[16]
                pid = fields[17]
                data_list.append((timestamp, action, protocol, sourceip, destip, sourceport, destport, size, tcpflags, tcpsyn, tcpack, tcpwin, icmptype, icmpcode, info, path, pid))   
                
    num_entries = len(data_list)
    if num_entries > 0:
        report = ArtifactHtmlReport('Windows Firewall Logs')
        report.start_artifact_report(report_folder, 'Windows Firewall Logs')
        report.add_script()
        data_headers = ('Timestamp', 'Action', 'Protocol', 'Source IP', 'Destination IP', 'Source Port', 'Dest Port', 'Size', 'TCP Flags', 'TCP SYN', 'TCP ACK', 'TCP WIN', 'ICMP Type', 'ICMP Code', 'Info', 'Path', 'PID')
        
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'Windows Firewall Logs'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = f'Windows Firewall Logs'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No Windows Firewall Logs data available')
        
    