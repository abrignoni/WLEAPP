import os
import xmltodict
import sqlite3

from bs4 import BeautifulSoup
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def get_windowsNotification(files_found, report_folder, seeker, wrap_text):

    for file_found in files_found:
        file_found = str(file_found)
        if not os.path.basename(file_found) == "wpndatabase.db":
            continue

        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        cursor.execute('''select Notification.Payload AS Payload,
        Notification.Type AS Type,
        datetime((Notification.ArrivalTime - 116444736000000000) / 10000000, 'unixepoch', 'localtime') AS ArrivalTime,
        datetime((Notification.ExpiryTime - 116444736000000000) / 10000000, 'unixepoch', 'localtime') AS ExpiryTime
        FROM Notification ORDER BY Notification.ArrivalTime ASC''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)

        if usageentries > 0:
            report = ArtifactHtmlReport('Windows Notification')
            report.start_artifact_report(report_folder, 'Windows Notification')
            report.add_script()

            data_list = []

            data_headers = ('Payload', 'Type', 'ExpiryTime', 'ArrivalTime')
            for rows in all_rows:
                try:
                    payload = rows[0].decode("utf-8")
                    payload_text = BeautifulSoup(payload, 'html.parser').text

                    data_list.append((payload_text, rows[1], rows[2], rows[3]))
                except:
                    pass

            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            tsvname = f'Windows Notification'
            tsv(report_folder, data_headers, data_list, tsvname)

        else:
            logfunc(f'No Windows Notification data available')

        db.close()