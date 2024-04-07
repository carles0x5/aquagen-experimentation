import os
import io
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import pandas as pd

class GoogleDrive:
    """Wrapper class for Google Drive API"""

    def __init__(self, credentials_path=None):
        """Initialize the Google Drive API"""
        self.service = self.authenticate_google_drive(credentials_path)

    def authenticate_google_drive(self, credentials_path=None):
        """Authenticate with Google Drive API"""
        scopes = ['https://www.googleapis.com/auth/drive']
        if not credentials_path:
            credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        credentials = service_account.Credentials.from_service_account_file(credentials_path, scopes=scopes)

        return build('drive', 'v3', credentials=credentials)
            
    def read_file(self, folder_id, filename):
        """Read an Excel file from Google Drive"""
        file_query = f"name = '{filename}' and '{folder_id}' in parents and trashed=false"
        files = self.service.files().list(
            q=file_query,
            fields='files(id)',
            includeItemsFromAllDrives=True,
            corpora='allDrives',
            supportsAllDrives=True).execute().get('files', [])
        
        if files:
            try:
                file_id = files[0]['id']
                request = self.service.files().get_media(fileId=file_id)
                file_content = request.execute()
                if filename.split('.')[1] in ['xlsx', 'csv']:
                    return io.BytesIO(file_content)
                else:
                    print("Unsupported file type")
                    return None
            except Exception as e:
                print(f"An error ocurred while reading {filename}: {e}")
                return None
        else:
            return None

    def write_file(self, file, folder_id, filename):
        # Set mime type for file type
        type_dict = {'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 
                     'csv': 'text/csv',
                     'jpg': 'image/jpeg'}
        file_type = filename.split('.')[1]
        mime_type = type_dict.get(file_type)

        # Save the DataFrame to a file in memory
        output = io.BytesIO()
        if file_type == 'xlsx':
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                file.to_excel(writer, index=False)
        elif file_type == 'csv':
            file.to_csv(output, index=False)
        elif file_type == 'jpg':
            img_bytes = io.BytesIO()
            file.savefig(img_bytes, format='jpg')
        output.seek(0)

        # Search for an existing file with the same name in the folder
        query = f"name = '{filename}' and '{folder_id}' in parents and trashed = false"
        response = self.service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
        files = response.get('files', [])

        # If file exists, update it. Otherwise, create a new file.
        try:
            media = MediaIoBaseUpload(output, mimetype=mime_type, resumable=True)
            if files:
                file_id = files[0].get('id')
                updated_file = self.service.files().update(
                    fileId=file_id, 
                    media_body=media, 
                    fields='id', 
                    supportsAllDrives=True).execute()
                return updated_file.get('id')
            else:
                file_metadata = {'name': filename, 'parents': [folder_id], 'mimeType': mime_type}
                created_file = self.service.files().create(
                    body=file_metadata, 
                    media_body=media, 
                    fields='id', 
                    supportsAllDrives=True).execute()
                return created_file.get('id')
        except Exception as e:
            print(f"An error ocurred while writing {filename}: {e}")


if __name__ == '__main__':
    gd = GoogleDrive()
    print("done")