import os
import re

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows

def get_setupapiDev(files_found, report_folder, seeker, wrap_text):

    for file_found in files_found:
        file_found = str(file_found)
        if not os.path.basename(file_found) == "setupapi.dev.log":
            continue

        with open(file_found, "r") as fp:
            data = fp.read()

        split_data = re.split("\[Device Install \(Hardware initiated\) - ", data)

        if len(split_data) > 0:
            del split_data[0] # index 0 is trash data
            report = ArtifactHtmlReport("setupapi.dev.log")
            report.start_artifact_report(report_folder, 'setupapi.dev.log')
            report.add_script()
        
            data_list = []

            data_headers = ('Name', 'First Connection Time')
            for i in split_data:
                name = i.split("]")[0]
                firstConnectionTime = i.split("Section start ")[1].split("\n")[0]
                data_list.append((name, firstConnectionTime))

            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            tsvname = f'setupapi.dev.log'
            tsv(report_folder, data_headers, data_list, tsvname)

        else:
            logfunc(f'No setupapi.dev.log data available')