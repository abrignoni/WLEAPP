import sqlite3
import os
import json

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def get_activitiesCache(files_found, report_folder, seeker, wrap_text):

    for file_found in files_found:
        file_found = str(file_found)
        
        if not os.path.basename(file_found) == 'ActivitiesCache.db':
            continue

        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        cursor.execute('''select Activity.AppActivityId AS AppActivityId,
        Activity.Payload AS Payload,
        datetime(Activity.LastModifiedTime, 'unixepoch', 'localtime') AS LastModifiedTime,
        datetime(Activity.ExpirationTime, 'unixepoch', 'localtime') AS ExpirationTime,
        datetime(Activity.StartTime, 'unixepoch', 'localtime') AS StartTime,
        datetime(Activity.EndTime, 'unixepoch', 'localtime') AS EndTime
        FROM Activity ORDER BY Activity.StartTime ASC''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)

        if usageentries > 0:
            report = ArtifactHtmlReport('ActivitiesCache')
            report.start_artifact_report(report_folder, 'ActivitiesCache')
            report.add_script()

            data_list = []

            data_headers = ('AppActivityId', 'DisplayText', 'AppDisplayName', 'LastModifiedTime', 'ExpirationTime', 'StartTime', 'EndTime')
            for rows in all_rows:
                try:
                    payload = rows[1].decode("utf-8")
                    payload = json.loads(payload)
                    displayText = payload.get('displayText')
                    appDisplayName = payload.get('appDisplayName')

                    data_list.append((rows[0], displayText, appDisplayName, rows[2], rows[3], rows[4], rows[5]))
                except:
                    pass

            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            tsvname = f'ActivitesCache'
            tsv(report_folder, data_headers, data_list, tsvname)

        else:
            logfunc(f'No ActivitiesCache data available')

        db.close()