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

reg = pd.read_csv('Event Registration.csv')

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

def download_file_from_drive(drive_url, output_file_path,download_progress_text,player_name):
    """
    Downloads a file from Google Drive using its URL.
    """
    # Extract the file ID from the Google Drive URL
    file_id = extract_file_id(drive_url)
    # print(f"Extracted file ID: {file_id}")
    # Request to download the file
    request = service.files().get_media(fileId=file_id)
    # Create a file handle for the output file
    with io.FileIO(output_file_path, 'wb') as file_handle:
        downloader = MediaIoBaseDownload(file_handle, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
            # {int(status.progress() * 100)}% 
            print(f"{download_progress_text} => {player_name}") 
    # print(f"File downloaded successfully and saved to {player_name}")

# Replace with your Google Drive file URL
# drive_url = 'https://drive.google.com/file/d/12UOFS5v4E0PCp3H2vW1ceabOsXGaIJZq/view?usp=sharing'
# output_file_path = 'downloaded_image.jpg'


total_players=reg.shape[0]

reg['Mobile Number'] = reg['Mobile Number'].astype('str')
reg['Flat number'] = reg['Flat number'].astype('str')
reg['player']=reg['Full Name']+'_'+ (reg['Flat number'])+'_'+ (reg['Mobile Number'])+'_'+  reg['Game Style']
init_player_counter=0
print("Total Enrollments: ",total_players)
print("Download Started:")
for player in reg[['Player profile pic','player']].values:
    init_player_counter=init_player_counter+1
    download_progress_text=f"{init_player_counter}/{total_players}"
    drive_url = f"https://drive.google.com/file/d/{player[0].partition('id=')[-1]}/view?usp=sharing" 
    output_file_path = '.\\enrolled_players\\'+player[1]+".jpg"
    # # Call the function to download the file
    download_file_from_drive(drive_url, output_file_path,download_progress_text,player[1])
print("Download Complete:")
