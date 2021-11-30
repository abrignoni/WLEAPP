import os

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def get_googleDrive(files_found, report_folder, seeker, wrap_text):

    for file_found in files_found:
        file_found = str(file_found)
        if not os.path.basename(file_found) == "metadata_sqlite_db":
            continue

        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()

        cursor.execute('''select items.local_title AS local_title,
        items.file_size AS file_size,
        items.mime_type AS mime_type,
        CASE
        WHEN items.trashed = 0 THEN 'No'
        WHEN items.trashed = 1 THEN 'Yes'
        ELSE 'Unknown'
        END AS trashed,
        CASE
        WHEN items.is_owner = 0 THEN 'No'
        WHEN items.is_owner = 1 THEN 'Yes'
        ELSE 'Unknown'
        END AS is_owner,
        datetime(ROUND("modified_date" / 1000), 'unixepoch', 'localtime') AS modified_date,
        datetime(ROUND("shared_with_me_date" / 1000), 'unixepoch', 'localtime') AS shared_with_me_date,
        datetime(ROUND("viewed_by_me_date" / 1000), 'unixepoch', 'localtime') AS viewed_by_me_date
        FROM items''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)

        if usageentries > 0:
            report = ArtifactHtmlReport('Google Drive')
            report.start_artifact_report(report_folder, 'Google Drive')
            report.add_script()

            data_list = []

            data_headers = ('local_title', 'file_size', 'mime_type', 'trashed', 'is_owner', 'modified_date', 'shared_with_me_date', 'viewed_by_me_date')
            for rows in all_rows:
                data_list.append((rows[0], rows[1], rows[2], rows[3], rows[4], rows[5], rows[6], rows[7]))

            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            tsvname = f'Google Drive'
            tsv(report_folder, data_headers, data_list, tsvname)

        else:
            logfunc(f'No Windows Google Drive data available')

        db.close()