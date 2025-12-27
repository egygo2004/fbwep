import os
from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.permission import Permission
from appwrite.role import Role

# Hardcoded for Setup Run
ENDPOINT = "https://nyc.cloud.appwrite.io/v1"
PROJECT_ID = "694f9a5d00376355b3a9"
API_KEY = "standard_00cc17f8d66b667767e1e356f91925a929f47a0f5ca17b42b95c95b286c31247c9691c6dcd9a4261d67977e115e709d0164accf2883f61581ed634a601ab0bb971ca02396d9edbe1022e60fa39aaaefa6021ef287fcdad8b212e25ecfc74882922c3a0ef5b4cb85907220826a110ac4fab9b8d7613a2500eda829d2a60e008ba"
DATABASE_ID = "694f9a8e00337e542bce"
COLLECTION_ID = "otp_logs"

# Initialize Client
client = Client()
client.set_endpoint(ENDPOINT)
client.set_project(PROJECT_ID)
client.set_key(API_KEY)

databases = Databases(client)

def setup_database():
    print(f"Initializing Appwrite Setup...")
    print(f"Project: {PROJECT_ID}")
    print(f"Database: {DATABASE_ID}")
    
    # 1. Check/Create Database
    try:
        databases.get(DATABASE_ID)
        print("✅ Database exists.")
    except Exception as e:
        print(f"⚠️ Database access failed: {e}")
    
    # 2. Check/Create Collection
    try:
        databases.get_collection(DATABASE_ID, COLLECTION_ID)
        print(f"✅ Collection '{COLLECTION_ID}' exists.")
    except:
        print(f"Creating collection '{COLLECTION_ID}'...")
        try:
            databases.create_collection(
                database_id=DATABASE_ID,
                collection_id=COLLECTION_ID,
                name="OTP Logs",
                permissions=[
                    Permission.read(Role.any()),
                    Permission.create(Role.any()),
                    Permission.update(Role.any()),
                    Permission.delete(Role.any())
                ]
            )
            print("✅ Collection created.")
        except Exception as e:
            print(f"❌ Failed to create collection: {e}")
            return

    # 3. Create Attributes
    attributes = [
        {"key": "phone", "type": "string", "size": 32, "required": True},
        {"key": "ip", "type": "string", "size": 64, "required": False},
        {"key": "step_1", "type": "string", "size": 32, "required": False},
        {"key": "step_2", "type": "string", "size": 32, "required": False},
        {"key": "step_3", "type": "string", "size": 32, "required": False}, # Search
        {"key": "step_4", "type": "string", "size": 32, "required": False}, # Result
        {"key": "step_5", "type": "string", "size": 32, "required": False}, # SMS
        {"key": "step_6", "type": "string", "size": 32, "required": False}, # Verify
        {"key": "status", "type": "string", "size": 32, "required": True},
        {"key": "otp_url", "type": "url", "required": False},
        {"key": "logs", "type": "string", "size": 5000, "required": False},
    ]

    print("Checking attributes...")
    for attr in attributes:
        try:
            if attr['type'] == 'string':
                databases.create_string_attribute(DATABASE_ID, COLLECTION_ID, attr['key'], attr['size'], attr['required'])
            elif attr['type'] == 'url':
                databases.create_url_attribute(DATABASE_ID, COLLECTION_ID, attr['key'], attr['required'])
        except Exception as e:
            if "already exists" in str(e):
                pass
            else:
                print(f"  ! Error creating '{attr['key']}': {e}")

    # ==========================================
    # 4. Command Queue Collection
    # ==========================================
    CMD_COLLECTION_ID = "command_queue"
    try:
        databases.get_collection(DATABASE_ID, CMD_COLLECTION_ID)
        print(f"✅ Collection '{CMD_COLLECTION_ID}' exists.")
    except:
        print(f"Creating collection '{CMD_COLLECTION_ID}'...")
        try:
            databases.create_collection(
                database_id=DATABASE_ID,
                collection_id=CMD_COLLECTION_ID,
                name="Command Queue",
                permissions=[
                    Permission.read(Role.any()),
                    Permission.create(Role.any()),
                    Permission.update(Role.any()),
                    Permission.delete(Role.any())
                ]
            )
            print(f"✅ Collection '{CMD_COLLECTION_ID}' created.")
        except Exception as e:
            print(f"❌ Failed to create command_queue: {e}")

    # Command Attributes
    cmd_attributes = [
        {"key": "type", "type": "string", "size": 64, "required": True},        # e.g., TEST_NUMBER
        {"key": "payload", "type": "string", "size": 255, "required": True},    # e.g., +123456
        {"key": "status", "type": "string", "size": 32, "required": True},      # PENDING, PROCESSING, COMPLETED
        {"key": "worker_id", "type": "string", "size": 64, "required": False},  # Who picked it up
    ]
    
    for attr in cmd_attributes:
        try:
            databases.create_string_attribute(DATABASE_ID, CMD_COLLECTION_ID, attr['key'], attr['size'], attr['required'])
            print(f"  + Cmd Attribute '{attr['key']}' created.")
        except Exception as e:
            if "already exists" in str(e):
                pass
            else:
                print(f"  ! Error creating cmd attr '{attr['key']}': {e}")

    
    print("\n🎉 Appwrite Setup Complete!")

if __name__ == "__main__":
    setup_database()
