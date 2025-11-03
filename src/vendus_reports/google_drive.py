"""Google Drive integration for uploading reports."""

import os
from io import BytesIO
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

# Google Drive API scopes
DRIVE_API_SCOPES = ["https://www.googleapis.com/auth/drive"]

# Environment variables
SERVICE_ACCOUNT_KEY_PATH = os.getenv("SERVICE_ACCOUNT_KEY_PATH")
ROOT_FOLDER_ID = os.getenv("ROOT_FOLDER_ID")
IMPERSONATED_EMAIL = os.getenv("IMPERSONATED_EMAIL")


def create_drive_service():
    """
    Creates and returns an authenticated Google Drive API service object.

    Returns:
        The authenticated Google Drive API service object
    """
    if not SERVICE_ACCOUNT_KEY_PATH:
        raise ValueError("SERVICE_ACCOUNT_KEY_PATH environment variable is required")
    if not IMPERSONATED_EMAIL:
        raise ValueError("IMPERSONATED_EMAIL environment variable is required")

    creds = Credentials.from_service_account_file(
        SERVICE_ACCOUNT_KEY_PATH, scopes=DRIVE_API_SCOPES
    )
    delegated_creds = creds.with_subject(IMPERSONATED_EMAIL)
    return build("drive", "v3", credentials=delegated_creds)


def create_folder_path(service, path_parts: list, root_folder_id: str) -> str:
    """
    Creates a folder structure based on a list of folder names.

    Args:
        service: The authenticated Google Drive API service object
        path_parts: A list of folder names representing the path
        root_folder_id: The ID of the root folder

    Returns:
        The ID of the deepest created folder
    """
    parent_folder_id = root_folder_id
    for folder_name in path_parts:
        parent_folder_id = create_or_get_folder(
            service, folder_name, parent_id=parent_folder_id
        )
    return parent_folder_id


def create_or_get_folder(service, folder_name: str, parent_id: str) -> str:
    """
    Creates a folder if it doesn't exist or retrieves its ID if it already exists.

    Args:
        service: The authenticated Google Drive API service object
        folder_name: The name of the folder
        parent_id: The ID of the parent folder

    Returns:
        The ID of the created or retrieved folder
    """
    query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'"
    query += f" and '{parent_id}' in parents"

    response = service.files().list(q=query, fields="files(id)").execute()
    folders = response.get("files", [])

    if folders:
        return folders[0]["id"]

    file_metadata = {
        "name": folder_name,
        "mimeType": "application/vnd.google-apps.folder",
    }
    if parent_id:
        file_metadata["parents"] = [parent_id]

    folder = service.files().create(body=file_metadata, fields="id").execute()
    return folder["id"]


def upload_file_to_drive(service, file_path: str, parent_folder_id: str):
    """
    Upload a file to Google Drive.

    Args:
        service: The authenticated Google Drive API service object
        file_path: Local path to the file to upload
        parent_folder_id: The ID of the parent folder

    Returns:
        The ID of the uploaded file
    """
    file_name = os.path.basename(file_path)

    # Determine MIME type based on file extension
    if file_path.endswith(".xml"):
        mime_type = "application/xml"
    elif file_path.endswith(".csv"):
        mime_type = "text/csv"
    else:
        mime_type = "text/plain"

    file_metadata = {
        "name": file_name,
        "parents": [parent_folder_id],
    }

    with open(file_path, "rb") as f:
        media = MediaIoBaseUpload(BytesIO(f.read()), mimetype=mime_type, resumable=True)

    file = (
        service.files()
        .create(body=file_metadata, media_body=media, fields="id")
        .execute()
    )

    return file.get("id")
