from google.oauth2 import service_account
from googleapiclient.discovery import build
import io
from googleapiclient.http import MediaIoBaseDownload
import re
import pandas as pd
import os

# Path to the JSON key file downloaded from Google Cloud
SERVICE_ACCOUNT_FILE = '.\\outh_client_secret.json'
def makedir(name):
    if not os.path.exists(name):
        os.makedirs(name)
        # print("Created new folder =", name)
makedir("enrolled_players")

# os.makedirs(os.path.dirname("enrolled_players"), exist_ok=True)

# Define the required scopes for accessing Google Drive
SCOPES = ['https://www.googleapis.com/auth/drive']

# Authenticate using the Service Account
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)

# Build the Google Drive API client
service = build('drive', 'v3', credentials=credentials)

def extract_file_id(drive_url):
    """
    Extracts the file ID from a Google Drive URL.
    """
    # Regex pattern to extract the file ID
    match = re.search(r'/d/([a-zA-Z0-9_-]+)', drive_url) or re.search(r'id=([a-zA-Z0-9_-]+)', drive_url)
    if match:
        return match.group(1)
    else:
        raise ValueError("Invalid Google Drive URL. Could not extract file ID.")

def download_file_from_drive(drive_url, output_file_path):
    """
    Downloads a file from Google Drive using its URL.
    """
    # Extract the file ID from the Google Drive URL
    file_id = extract_file_id(drive_url)
    print(f"Extracted file ID: {file_id}")

    # Request to download the file
    request = service.files().get_media(fileId=file_id)

    # Create a file handle for the output file
    with io.FileIO(output_file_path, 'wb') as file_handle:
        downloader = MediaIoBaseDownload(file_handle, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
            print(f"Download progress: {int(status.progress() * 100)}%")

    print(f"File downloaded successfully and saved to {output_file_path}")

# Replace with your Google Drive file URL
# drive_url = 'https://drive.google.com/file/d/12UOFS5v4E0PCp3H2vW1ceabOsXGaIJZq/view?usp=sharing'
# output_file_path = 'downloaded_image.jpg'

reg = pd.read_csv('EventRegistration.csv')
reg['Mobile Number'] = reg['Mobile Number'].astype('str')
reg['Wing Number'] = reg['Wing Number'].astype('str')
reg['player']=reg['Full Name']+'_'+ (reg['Wing Number'])+'_'+ (reg['Mobile Number'])+'_'+  reg['Game Style']
for player in reg[['Player profile pic','player']].values:
    drive_url = f"https://drive.google.com/file/d/{player[0].partition('&id=')[-1]}/view?usp=sharing"  
    output_file_path = '.\\enrolled_players\\'+player[1]+".jpg"
    # Call the function to download the file
    download_file_from_drive(drive_url, output_file_path)

