import os
from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.query import Query

# Configuration (Hardcoded from fb_otp_browser.py)
APPWRITE_ENDPOINT = 'https://nyc.cloud.appwrite.io/v1'
APPWRITE_PROJECT_ID = '694f9a5d00376355b3a9'
APPWRITE_API_KEY = 'standard_00cc17f8d66b667767e1e356f91925a929f47a0f5ca17b42b95c95b286c31247c9691c6dcd9a4261d67977e115e709d0164accf2883f61581ed634a601ab0bb971ca02396d9edbe1022e60fa39aaaefa6021ef287fcdad8b212e25ecfc74882922c3a0ef5b4cb85907220826a110ac4fab9b8d7613a2500eda829d2a60e008ba'
APPWRITE_DATABASE_ID = '694f9a8e00337e542bce'
APPWRITE_CMD_COLLECTION_ID = 'command_queue'

# Setup Appwrite
client = Client()
client.set_endpoint(APPWRITE_ENDPOINT)
client.set_project(APPWRITE_PROJECT_ID)
client.set_key(APPWRITE_API_KEY)

databases = Databases(client)

def clear_queue():
    print("🔍 Fetching pending commands...")
    
    # List all PENDING commands
    # Note: Default limit is 25, might need pagination if queue is huge
    queries = [
        Query.equal("status", "PENDING"),
        Query.limit(100) 
    ]
    
    result = databases.list_documents(
        APPWRITE_DATABASE_ID,
        APPWRITE_CMD_COLLECTION_ID,
        queries
    )
    
    total = result['total']
    docs = result['documents']
    
    if total == 0:
        print("✅ Queue is already empty.")
        return

    print(f"⚠️ Found {total} pending commands. Clearing...")
    
    count = 0
    for doc in docs:
        try:
            # We can either delete them or mark as CANCELLED
            # Deleting is cleaner for "Stop" request
            databases.delete_document(
                APPWRITE_DATABASE_ID,
                APPWRITE_CMD_COLLECTION_ID,
                doc['$id']
            )
            count += 1
            print(f"Deleted {doc['$id']} ({count}/{len(docs)})")
        except Exception as e:
            print(f"Failed to delete {doc['$id']}: {e}")

    print(f"🎉 Successfully cleared {count} commands!")

if __name__ == "__main__":
    clear_queue()
