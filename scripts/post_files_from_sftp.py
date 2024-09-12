"""
Utility to chuck files from the sftp server at cupid.
"""


from fabric import Connection
from dotenv import dotenv_values
import gnupg
import os
from pathlib import Path
import requests

ENV = dotenv_values(".env.scripts")
sftp_path = "/data/rdastaging/archive"
local_folder = Path(".xml_errors")
#GNUPG_HOME = '~/.gnupg'

#gpg = gnupg.GPG()

# Create local_folder if it doesn't exist
os.makedirs(local_folder, exist_ok=True)

# Establish SSH connection and download the encrypted file
with Connection(
    host=ENV["SFTP_HOST"], 
    user=ENV["SFTP_USER"], 
    connect_kwargs={'password': ENV["SFTP_PASSWORD"]}
) as c:
    # List files from SFTP server
    sftp_files = c.run(f'find {sftp_path} -name "*.xml.gpg"', hide=True).stdout.split()
    
    for sftp_file in sftp_files:#sftp_files[:1000]:
        #local_file_path = os.path.join(local_folder, os.path.basename(sftp_file))
        #c.get(sftp_file, local_file_path)

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
                print(response.content)
                continue

            # Try to upload xml file 
            response = requests.post(upload_url, headers=headers, data=decrypted_data)
            
            # Check the response status
            print(response.content)
            if response.status_code !=200: 
                file_name = f"{sftp_file.split('/')[-1].split('.')[0]}.xml" 
                file_path = local_folder / file_name
                with open(file_path, "w") as f:
                    f.write(decrypted_data)
