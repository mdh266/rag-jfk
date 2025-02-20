from dotenv import load_dotenv
load_dotenv()
from google.oauth2 import service_account
from google.cloud import storage
import os


def main():
    """
    Subset only the speeches when kennedy was president
    """
    credentials = service_account.Credentials.from_service_account_file('credentials.json')
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "credentials.json"


    client = storage.Client(project=credentials.project_id,
                            credentials=credentials)

    fullbucket = client.get_bucket("kennedyskis")

    # get only speeches when JFK was president
    presidential_speeches = [
    blob.name for blob in  bucket.list_blobs() 
         if "1961" in blob.name or 
            "1962" in blob.name or 
            "1963" in blob.name
    ]

    # create new bucket 
    subbucket = client.create_bucket("prezkennedyspeches")

    # copy over the json
    for speech in presidential_speeches:
        blob = bucket.get_blob(speech)
        new_bucket.blob(speech).upload_from_string(data=blob.download_as_string())


if __name__ == "__main__":
    main()
