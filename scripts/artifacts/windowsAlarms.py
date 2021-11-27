import json
import os
import datetime
import pyregf

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows

# https://gist.github.com/NotWearingPants/d162aaf32aef0227bf6bbd37b7317633
FILE_TIME_EPOCH = datetime.datetime(1601, 1, 1)
FILE_TIME_MICROSECOND = 10

def convert_from_file_time(file_time):
    microseconds_since_file_time_epoch = file_time // FILE_TIME_MICROSECOND
    return FILE_TIME_EPOCH + datetime.timedelta(microseconds=microseconds_since_file_time_epoch)

def getData(data, value):
    data_idx = data.find(value.encode("utf-16")[2:]) # remove \xff\xfe
    result = data[data_idx+len(value)*2+2:]

    if value == "__Created" or value == "__Updated":
        return convert_from_file_time(int.from_bytes(result[:8], 'little'))
    elif value == "Name":
        return result[:result.find(b"\x00\x00")] + b"\x00"
    else:
        return int.from_bytes(result[:result.find(b"\x00\x00")], 'little')

def get_windowsAlarms(files_found, report_folder, seeker, wrap_text):
    # TODO: Write code to parse the structure

    for file_found in files_found:
        file_found = str(file_found)
        if os.path.basename(file_found) == "Alarms.json":
            with open(file_found, "r", encoding="utf-8") as fp:
                jsonData = json.load(fp)

            data_list = []
            for value in jsonData['Alarms']:
                name = value.get('Name')
                hour = value.get('Hour')
                minute = value.get('Minute')
                isEnabled = value.get('IsEnabled')
                isRecurring = value.get('IsRecurring')
                snoozeInterval = value.get('SnoozeInterval')

            data_list.append((name, hour, minute, isEnabled, isRecurring, snoozeInterval))

            num_entries = len(data_list)
            if num_entries > 0:
                report = ArtifactHtmlReport('Windows Alarms - json')
                report.start_artifact_report(report_folder, 'Windows Alarms - json')
                report.add_script()
                data_headers = ('Name', 'Hour', 'Minute', 'IsEnabled', 'IsRecurring', 'SnoozeInterval')

                report.write_artifact_data_table(data_headers, data_list, file_found)
                report.end_artifact_report()

                tsvname = f'Windows Alarms - json'
                tsv(report_folder, data_headers, data_list, tsvname)
            else:
                logfunc('No Windows Alarms - json data available')

        elif os.path.basename(file_found) == "settings.dat":
            data_list = []
            regf_file = pyregf.file()
            regf_file.open(file_found)
            key = regf_file.get_key_by_path("\\LocalState\\Alarms")
            for idx in range(0, key.get_number_of_values()):
                rawData = key.get_value(idx).get_data()
            
                name = getData(rawData, "Name").decode("utf-16")
                hour = getData(rawData, "Hour")
                minute = getData(rawData, "Minute")
                isEnabled = getData(rawData, "IsEnabled")
                daysOfWeek = getData(rawData, "DaysOfWeek")
                snoozeInterval = getData(rawData, "SnoozeInterval")
                scheduledHour = getData(rawData, "ScheduledHour")
                scheduledMinute = getData(rawData, "ScheduledMinute")
                scheduledDay = getData(rawData, "ScheduledDay")
                scheduledMonth = getData(rawData, "ScheduledMonth")
                scheduledYear = getData(rawData, "ScheduledYear")
                createdValue = getData(rawData, "__Created")
                updatedValue = getData(rawData, "__Updated")
                data_list.append((name, hour, minute, isEnabled, daysOfWeek, snoozeInterval, scheduledHour, scheduledMinute, scheduledDay, scheduledMonth, scheduledYear, createdValue, updatedValue))
            regf_file.close()

            num_entries = len(data_list)
            if num_entries > 0:
                report = ArtifactHtmlReport('Windows Alarms - registry')
                report.start_artifact_report(report_folder, 'Windows Alarms - registry')
                report.add_script()
                data_headers = ('Name', 'Hour', 'Minute', 'IsEnabled', 'DaysOfWeek', 'SnoozeInterval', 'ScheduledHour', 'ScheduledMinute', 'ScheduledDay', 'ScheduledMonth', 'ScheduledYear', 'Created', 'Updated')

                report.write_artifact_data_table(data_headers, data_list, file_found)
                report.end_artifact_report()

                tsvname = f'Windows Alarms - registry'
                tsv(report_folder, data_headers, data_list, tsvname)
            else:
                logfunc('No Windows Alarms - registry data available')