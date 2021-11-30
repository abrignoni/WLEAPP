import os
import datetime
import re

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def get_facebookMessenger(files_found, report_folder, seeker, wrap_text):

    for file_found in files_found:
        file_found = str(file_found)
        if not re.search(r"msys_[0-9]*.db", file_found):
            continue

        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()

        cursor.execute('''select 
            contacts.name AS name,
			contacts.username AS usernmae,
            thread_messages.text AS text,
            datetime(ROUND(thread_messages.timestamp_ms / 1000), 'unixepoch', 'localtime') AS timestamp,
            thread_messages.nullstate_description_text1 AS description1,
            thread_messages.nullstate_description_text2 AS description2,
            thread_messages.nullstate_description_text3 AS description3,
			thread_messages.profile_picture_url AS profile_picture_url
            from thread_messages join contacts on contacts.id = thread_messages.sender_id
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)

        if usageentries > 0:
            report = ArtifactHtmlReport('Facebook Messenger - Messages')
            report.start_artifact_report(report_folder, 'Facebook Messenger - Messages')
            report.add_script()

            data_list = []

            data_headers = ('name', 'username', 'text', 'timestamp', 'description1', 'description2', 'description3', 'profile_picture_url')
            for rows in all_rows:
                data_list.append((rows[0], rows[1], rows[2], rows[3], rows[4], rows[5], rows[6], rows[7]))

            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            tsvname = f'Facebook Messenger - Messages'
            tsv(report_folder, data_headers, data_list, tsvname)

        else:
            logfunc(f'No Facebook Messenger - Messages available')

        cursor.execute('''select 
            bucket_stories.bucket_id AS bucket_id,
            bucket_stories.owner_id AS owner_id,
            bucket_stories.bucket_name AS bucket_name,
            datetime(ROUND(bucket_stories.timestamp_ms / 1000), 'unixepoch', 'localtime') AS timestamp,
            bucket_stories.media_url AS media_url,
            bucket_stories.media_playable_url AS media_playable_url,
            bucket_stories.media_thumbnail_url AS media_thumbnail_url
            from bucket_stories ORDER BY timestamp ASC
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)

        if usageentries > 0:
            report = ArtifactHtmlReport('Facebook Messenger - Stories')
            report.start_artifact_report(report_folder, 'Facebook Messenger - Stories')
            report.add_script()

            data_list = []

            data_headers = ('bucket_id', 'owner_id', 'bucket_name', 'media_url', 'media_playable_url', 'media_thumbnail_url', 'timestamp')
            for rows in all_rows:
                data_list.append((rows[0], rows[1], rows[2], rows[3], rows[4], rows[5], rows[6]))

            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            tsvname = f'Facebook Messenger - Stories'
            tsv(report_folder, data_headers, data_list, tsvname)

        else:
            logfunc(f'No Facebook Messenger - Stories available')

        cursor.execute('''select 
            contacts.id AS id,
            contacts.username AS username,
            contacts.name AS name,
            contacts.first_name AS first_name,
            contacts.last_name AS last_name,
            strftime('%m/%d', contacts.birthday_timestamp, 'unixepoch') AS birthday,
            CASE
            WHEN contacts.is_messenger_user = 0 THEN 'No'
            WHEN contacts.is_messenger_user = 1 THEN 'Yes'
            ELSE 'Unknown'
            END AS is_messenger_user,
            contacts.profile_picture_url AS profile_picture_url,
            contacts.profile_picture_large_url AS profile_picture_large_url
            from contacts
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)

        if usageentries > 0:
            report = ArtifactHtmlReport('Facebook Messenger - Contacts')
            report.start_artifact_report(report_folder, 'Facebook Messenger - Contacts')
            report.add_script()

            data_list = []

            data_headers = ('id', 'username', 'name', 'first_name', 'last_name', 'birthday', 'is_messenger_user', 'profile_picture_url', 'profile_picture_large_url')
            for rows in all_rows:
                data_list.append((rows[0], rows[1], rows[2], rows[3], rows[4], rows[5], rows[6], rows[7], rows[8]))

            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            tsvname = f'Facebook Messenger - Contacts'
            tsv(report_folder, data_headers, data_list, tsvname)

        else:
            logfunc(f'No Facebook Messenger - Contacts available')

        cursor.execute('''select 
            attachments.filename AS filename,
            attachments.filesize AS filesize,
            datetime(ROUND(attachments.timestamp_ms / 1000), 'unixepoch', 'localtime') AS timestamp,
            attachments.playable_url AS playable_url,
            attachments.playable_url_mime_type AS playable_url_mime_type,
            attachments.accessibility_summary_text AS summary_text
            from attachments ORDER BY timestamp ASC
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)

        if usageentries > 0:
            report = ArtifactHtmlReport('Facebook Messenger - Attachments')
            report.start_artifact_report(report_folder, 'Facebook Messenger - Attachments')
            report.add_script()

            data_list = []

            data_headers = ('filename', 'filesize', 'timestamp', 'playable_url', 'playable_url_mime_type', 'summary_text')
            for rows in all_rows:
                data_list.append((rows[0], rows[1], rows[2], rows[3], rows[4], rows[5]))

            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            tsvname = f'Facebook Messenger - Attachments'
            tsv(report_folder, data_headers, data_list, tsvname)

        else:
            logfunc(f'No Facebook Messenger - Attachments available')

        db.close()