import sqlite3
import os
import re

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def get_windowsStickyNotes(files_found, report_folder, seeker, wrap_text):

    for file_found in files_found:
        file_found = str(file_found)
        if not os.path.basename(file_found) == "plum.sqlite":
            continue

        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        cursor.execute('''select Note.Text,
        CASE
        WHEN Note.IsOpen = 0 THEN 'No'
        WHEN Note.IsOpen = 1 THEN 'Yes'
        ELSE 'Unknown'
        END AS IsOpen,
        CASE
        WHEN Note.IsAlwaysOnTop = 0 THEN 'No'
        WHEN Note.IsAlwaysOnTop = 1 THEN 'Yes'
        ELSE 'Unknown'
        END AS IsAlwaysOnTop,
        Note.Theme AS Theme,
        datetime(("CreatedAt" / 10000000) - 62135596800, 'unixepoch', 'localtime') AS CreatedAt,
        datetime(("UpdatedAt" / 10000000) - 62135596800, 'unixepoch', 'localtime') AS UpdatedAt,
        datetime(("DeletedAt" / 10000000) - 62135596800, 'unixepoch', 'localtime') AS DeletedAt
        FROM Note ORDER BY Note.CreatedAt ASC''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)

        if usageentries > 0:
            report = ArtifactHtmlReport('Windows StickyNotes')
            report.start_artifact_report(report_folder, 'Windows StickyNotes')
            report.add_script()

            data_list = []

            data_headers = ('Text', 'IsOpen', 'IsAlwaysOnTop', 'Theme', 'CreatedAt', 'UpdatedAt', 'DeletedAt')
            for rows in all_rows:
                text_data = re.sub("\\\\id=[A-Za-z0-9]{8}-[A-Za-z0-9]{4}-[A-Za-z0-9]{4}-[A-Za-z0-9]{4}-[A-Za-z0-9]{12} ","",rows[0])
                data_list.append((text_data, rows[1], rows[2], rows[3], rows[4], rows[5], rows[6]))

            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            tsvname = f'Windows StickyNotes'
            tsv(report_folder, data_headers, data_list, tsvname)

        else:
            logfunc(f'No Windows StickyNotes data available')

        db.close()