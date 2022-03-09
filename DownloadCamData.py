from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

import os

DATA_FOLDER = '/Users/arthurliu/Documents/InsectRobotics/plant-live-viewing-data/data'

def download_files():
    gauth = GoogleAuth()
    drive = GoogleDrive(gauth)

    team_drive_id = '0AD1fLQRzTm-GUk9PVA'
    parent_folder_id = '1w_nja_Sb5n2b2hNgVureqgYjr8N2EYMG'

    file_list = drive.ListFile({
        'q': f"'{parent_folder_id}' in parents and trashed=false",
        'supportsAllDrives': True,
        'driveId': team_drive_id,
        'includeItemsFromAllDrives': True,
        'corpora': 'drive'
    }).GetList()
    
    downloaded_files = os.listdir(DATA_FOLDER)

    for i, file in enumerate(file_list):
        if file['title'] not in downloaded_files:
            print(f"{i}: Downloading {file['title']}")
            filename_to_save = os.path.join(DATA_FOLDER, file['title'])
            file.GetContentFile(filename_to_save)

    print("Completed")

if __name__=="__main__":
    download_files()