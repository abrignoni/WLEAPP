import sqlite3
import os

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def get_windowsPhotos(files_found, report_folder, seeker, wrap_text):

    for file_found in files_found:
        file_found = str(file_found)
        if not os.path.basename(file_found) == "MediaDb.v1.sqlite":
            continue

        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        try:
            cursor.execute('''select item.Item_FileName AS Item_FileName,
            item.Item_FileSize AS Item_FileSize,
            item.Item_Width AS Item_Width,
            item.Item_Height AS Item_Height,
            datetime((item.Item_DateTaken - 116444736000000000) / 10000000, 'unixepoch', 'localtime') AS Item_DateTaken,
            datetime((item.Item_DateCreated - 116444736000000000) / 10000000, 'unixepoch', 'localtime') AS Item_DateCreated,
            datetime((item.Item_DateModified - 116444736000000000) / 10000000, 'unixepoch', 'localtime') AS Item_DateModified,
            datetime((item.Item_DateIngested - 116444736000000000) / 10000000, 'unixepoch', 'localtime') AS Item_DateIngested
            FROM item ORDER BY Item_DateCreated ASC''')

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
        except:
            usageentries = 0

        if usageentries > 0:
            report = ArtifactHtmlReport("Windows Photos - Item")
            report.start_artifact_report(report_folder, 'Windows Photos - Item')
            report.add_script()

            data_list = []

            data_headers = ('Filename', 'Filesize', 'Width', 'Height', 'DateTaken', 'DateCreated', 'DateModified', 'DateIngested')
            for rows in all_rows:
                data_list.append((rows[0], rows[1], rows[2], rows[3], rows[4], rows[5], rows[6], rows[7]))

            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            tsvname = f'Windows Photos - Item'
            tsv(report_folder, data_headers, data_list, tsvname)

        else:
            logfunc(f'No Item table available')

        try:
            cursor.execute('''select Folder.Folder_Path AS Folder_Path,
            Folder.Folder_DisplayName AS Folder_DisplayName,
            Folder.Folder_ItemCount AS Folder_ItemCount,
            datetime((Folder.Folder_DateCreated - 116444736000000000) / 10000000, 'unixepoch', 'localtime') AS Folder_DateCreated,
            datetime((Folder.Folder_DateModified - 116444736000000000) / 10000000, 'unixepoch', 'localtime') AS Folder_DateModified
            FROM Folder ORDER BY Folder_DateCreated ASC''')
            
            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
        except:
            usageentries = 0

        if usageentries > 0:
            report = ArtifactHtmlReport("Windows Photos - Folder")
            report.start_artifact_report(report_folder, 'Windows Photos - Folder')
            report.add_script()

            data_list = []

            data_headers = ("Folder_Path", "Folder_DisplayName", "Folder_ItemCount", "Folder_DateCreated", "Folder_DateModified")
            for rows in all_rows:
                data_list.append((rows[0], rows[1] ,rows[2], rows[3], rows[4]))

            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            tsvname = f'Windows Photos - Folder'
            tsv(report_folder, data_headers, data_list, tsvname)
            
        else:
            logfunc(f"No Folder table available")

        db.close()