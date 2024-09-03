from google.oauth2 import service_account
from google.auth.transport.requests import AuthorizedSession
import json
from app.config import settings
from sqlalchemy.orm import Session
from ..models import DeletedUsers

# Define the required scopes
scopes = [
    "https://www.googleapis.com/auth/firebase.database",
    "https://www.googleapis.com/auth/cloud-platform"
]

# Authenticate a credential with the service account
credentials = service_account.Credentials.from_service_account_file(
    "./venv/serviceAccountKey.json", scopes=scopes)

# Use the credentials object to authenticate a Requests session.
authed_session = AuthorizedSession(credentials)

# Replace these values with your actual information
project_id = settings.firebase_project_id


# Build the URL for the Firestore document
base_url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents"


def delete_user_info(user_id: str, db: Session):
    document_path = f"users/{user_id}"
    document_url = f"{base_url}/{document_path}"

    # Archive user details
    try:
        res = authed_session.get(document_url).json()
        deleted_user = DeletedUsers(firebase_uid=user_id, 
                                    auth_type=res['fields']['authenticationType']['stringValue'], 
                                    first_name = res['fields']['firstName']['stringValue'],
                                    last_name = res['fields']['lastName']['stringValue'],
                                    email = res['fields']['email']['stringValue'],
                                    phone = res['fields']['phoneNo']['stringValue'])
        db.add(deleted_user)
        db.commit()
    except Exception:
        pass

    # Make a DELETE request to delete the document
    response = authed_session.delete(document_url)

    # Check the response status
    if response.status_code == 200:
        print("Document deleted successfully.")
    else:
        print(f"Failed to delete document. Status code: {response.status_code}")
        print(response.text)
