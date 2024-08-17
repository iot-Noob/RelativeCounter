import os
from dotenv import load_dotenv

load_dotenv(override=True,verbose=True)

try:

    csv_path=os.getenv("FILE_NAME")

except Exception as e:
    print(f"Error load env due to {e}")