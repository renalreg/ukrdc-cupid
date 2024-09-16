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

def print_loading_bar(iteration, total, length=10):
    """Print a simple loading bar using the print statement."""
    percent = int(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = "#" * filled_length + '-' * (length - filled_length)
    print(f"\r[{bar}] {percent}%", end='')


ENV = dotenv_values(".env.scripts")
sftp_path = "/data/rdastaging/archive"
local_folder = Path(".xml_errored")
#GNUPG_HOME = '~/.gnupg'

#gpg = gnupg.GPG()

# Create local_folder if it doesn't exist
os.makedirs(local_folder, exist_ok=True)

# Establish SSH connection and download the encrypted file
t0 = time()
with Connection(
    host=ENV["SFTP_HOST"], 
    user=ENV["SFTP_USER"], 
    connect_kwargs={'password': ENV["SFTP_PASSWORD"]}
) as c:
    # List files from SFTP server
    sftp_files = c.run(f'find {sftp_path} -name "*.xml.gpg"', hide=True).stdout.split()
    number_of_files = len(sftp_files)
    number_of_files = 5000
    response_cache = defaultdict(int)
    print(f"Loading {number_of_files} files")
    for i, sftp_file in enumerate(sftp_files[:number_of_files]):
    #for i, sftp_file in enumerate(sftp_files):
        #local_file_path = os.path.join(local_folder, os.path.basename(sftp_file))
        #c.get(sftp_file, local_file_path)

        print_loading_bar(i,number_of_files)
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
            post_url = ENV["CUPID_URL"]
            validation_url = post_url + "/parse/xml_validate/4.2.0"
            upload_url = post_url + "/store/upload_patient_file/overwrite"
            headers = {
                "Content-Type": "application/xml"
            }
            
            # validate against schema
            response = requests.post(validation_url, headers=headers, data=decrypted_data)

            if response.status_code != 200:
                #print(response.content)
                response_cache[response.content]+=1
                continue

            # Try to upload xml file 
            response = requests.post(upload_url, headers=headers, data=decrypted_data)
            
            # Check the response status
            #print(response.content)
            if response.status_code !=200:
                file_name = f"{sftp_file.split('/')[-1].split('.')[0]}.xml" 
                file_path = local_folder / file_name
                with open(file_path, "w") as f:
                    f.write(decrypted_data)
            
            response_cache[response.content]+=1

time_mins = (time() - t0) / 60.
report = f"""
Time taken : {time_mins:.2f}
"""
for key, value in response_cache.items():
    report = report + f"{value} : {key} "

print(report)