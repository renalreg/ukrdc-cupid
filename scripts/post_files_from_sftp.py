"""
Utility to chuck files from the sftp server at cupid.
"""

import os
import requests

from time import time
from collections import defaultdict
from pathlib import Path
from fabric import Connection
from dotenv import dotenv_values

def print_loading_bar(iteration, total, length=20):
    """Print a simple loading bar using the print statement."""
    percent = int(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = "#" * filled_length + '-' * (length - filled_length)
    print(f"\r[{bar}] {percent}%", end='')


ENV = dotenv_values(".env.scripts")
sftp_path = "/data/rdastaging/archive"
errored_files_folder = Path(".xml_errored")
decrypted_folder = Path(".xml_decrypted")

LOAD_FILES_FROM_SFTP = False

# Create local_folder if it doesn't exist
os.makedirs(errored_files_folder, exist_ok=True)
os.makedirs(decrypted_folder, exist_ok=True)

# Establish SSH connection and download and decrypt files and dump them into a
# folder
if LOAD_FILES_FROM_SFTP:
    with Connection(
        host=ENV["SFTP_HOST"], 
        user=ENV["SFTP_USER"], 
        connect_kwargs={'password': ENV["SFTP_PASSWORD"]}
    ) as c:
        # List files from SFTP server
        sftp_files = c.run(f'find {sftp_path} -name "*.xml.gpg"', hide=True).stdout.split()
        number_of_files = len(sftp_files)

        print(f"Downloading {number_of_files} files")
        for i, sftp_file in enumerate(sftp_files):
            #local_file_path = os.path.join(local_folder, os.path.basename(sftp_file))
            #c.get(sftp_file, local_file_path)

            print_loading_bar(i, number_of_files)
            # Decrypt the file on the remote server 
            passphrase = ENV["GPG_PASSPHRASE"]
            decrypt_command = (
                f"gpg --batch --yes --passphrase '{passphrase}' --decrypt {sftp_file}"
            )

            try:
                # decrypt and capture stdout
                decrypted_data = c.run(decrypt_command, hide=True).stdout
            except:
                # if it doesn't work we don't sweat
                continue
            else:
                # save file locally
                decrypted_file_name = Path(sftp_file).stem
                decrypted_file_path = decrypted_folder / decrypted_file_name
                
                with open(decrypted_file_path, "w") as decrypted_file:
                        decrypted_file.write(decrypted_data)


# Load files from folder and time how long it takes cupid to rinse through it
response_cache = defaultdict(int)
xml_to_load = [file for file in decrypted_folder.glob("*.xml")]
#xml_to_load = xml_to_load[:100]
t0 = time()
files_to_load = len(xml_to_load)

total_thinking_time = time() - time()
if files_to_load == 0:
    print("Downloaded XML folder seems to be empty. Try setting LOAD_FILES_FROM_SFTP = True.")
else:
    print(f"Loading {files_to_load} files into Cupid")
    for i, xml_file in enumerate(xml_to_load):
        print_loading_bar(i, files_to_load)
        with open(xml_file) as file:
            data = file.read()

        post_url = ENV["CUPID_POST_URL"]
        validation_url = post_url + "/parse/xml_validate/4.2.0"
        upload_url = post_url + "/store/upload_patient_file/overwrite"
        headers = {
            "Content-Type": "application/xml"
        }           
        # validate against schema
        response = requests.post(validation_url, headers=headers, data=data)
        if response.status_code != 200:
            response_cache[response.content]+=1
            continue

        # Try to upload xml file 
        t0 = time()
        response = requests.post(upload_url, headers=headers, data=data)
        time_diff = time() - t0
        total_thinking_time += time_diff  
          
                
        # Check the response status
        if response.status_code !=200:
            errored_file_path = errored_files_folder / xml_file.name
            with open(errored_file_path, "w") as f:
                f.write(data)
                response_cache[response.content]+=1


report = f"""
Average per file : {total_thinking_time/files_to_load:.2f} secs
"""
for key, value in response_cache.items():
    if value > 1:
        report = report + f"{value} : {key} \n"

print(report)