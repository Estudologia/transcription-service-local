import os
import csv
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def list_files_in_folder(folder_id):
    query = f"'{folder_id}' in parents and mimeType != 'application/vnd.google-apps.folder' and trashed = false"
    results = drive_service.files().list(q=query, fields="nextPageToken, files(id, name, mimeType)").execute()
    return results.get('files', [])

def save_to_csv(file_list, file_name):
    with open(file_name, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['file_name', 'file_id', 'mime_type']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for file in file_list:
            writer.writerow({'file_name': file['name'], 'file_id': file['id'], 'mime_type': file['mimeType']})

SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = 'serious-app-384900-0f5abc063d70.json'
folder_id = '1u139qyl5MekYvO90Kz9hVd09E4iVMlLn'

creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
drive_service = build('drive', 'v3', credentials=creds)

try:
    file_list = list_files_in_folder(folder_id)
    csv_file_name = 'drive_folder_files.csv'
    save_to_csv(file_list, csv_file_name)
    print(f'Arquivo CSV gerado: {csv_file_name}')
except HttpError as error:
    print(f'An error occurred: {error}')
