import os
import re
import json
import datetime
import ast

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows

# https://gist.github.com/NotWearingPants/d162aaf32aef0227bf6bbd37b7317633
FILE_TIME_EPOCH = datetime.datetime(1601, 1, 1)
FILE_TIME_MICROSECOND = 10

def convert_from_file_time(file_time):
    microseconds_since_file_time_epoch = file_time // FILE_TIME_MICROSECOND
    return FILE_TIME_EPOCH + datetime.timedelta(microseconds=microseconds_since_file_time_epoch)

def getData(data, value):
    try:
        return data.get(value).get("Value")
    except:
        return None

def convertDateTime(date):
    try:
        return convert_from_file_time(float(date))
    except:
        return None

def get_windowsCortana(files_found, report_folder, seeker, wrap_text):

    for file_found in files_found:
        file_found = str(file_found)
        if not re.search(r"AppCache[0-9]*.txt", file_found):
            continue

        with open(file_found, "r", encoding="utf-8") as fp:
            json_data = json.loads(fp.read())
            if json_data:
                report = ArtifactHtmlReport('DeviceSearchCache')
                report.start_artifact_report(report_folder, 'DeviceSearchCache')
                report.add_script()

                data_list = []
                data_headers = ('ParsingName', 'TimesUsed', 'Filename', 'Name', 'Path', 'Description', 'Date', 'DateAccessed', 'EncodedTargetParh', 'ItemNameDisplay')

                for data in json_data:
                    name = ''
                    path = ''
                    description = ''
                    date = ''

                    jumplist_data = getData(data, 'System.ConnectedSearch.JumpList')
                    jumplist_list = ast.literal_eval(jumplist_data.replace("\\", "/"))
                    if len(jumplist_list) > 0:
                        for i in jumplist_list[0]['Items']:
                            name = i.get('Name')
                            path = i.get('Path')
                            description = i.get('Description')
                            date = i.get('Date')

                            data_list.append((
                                getData(data,'System.ParsingName'),
                                getData(data,'System.Software.TimesUsed'),
                                getData(data,'System.FileName'),
                                name, path, description, date,
                                convertDateTime(getData(data,'System.DateAccessed')),
                                getData(data,'System.Tile.EncodedTargetPath'),
                                getData(data,'System.ItemNameDisplay')
                            ))
                    else:
                        data_list.append((
                            getData(data,'System.ParsingName'),
                            getData(data,'System.Software.TimesUsed'),
                            getData(data,'System.FileName'),
                            name, path, jumplist_data, date,
                            convertDateTime(getData(data,'System.DateAccessed')),
                            getData(data,'System.Tile.EncodedTargetPath'),
                            getData(data,'System.ItemNameDisplay')
                        ))

                report.write_artifact_data_table(data_headers, data_list, file_found)
                report.end_artifact_report()

                tsvname = f'DeviceSearchCache'
                tsv(report_folder, data_headers, data_list, tsvname)
            else:
                logfunc(f'No DeviceSearchCache data available')