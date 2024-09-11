"""
Utility to chuck files from the sftp server at cupid.
"""


from fabric import Connection
from dotenv import dotenv_values
import gnupg
import os
import requests

ENV = dotenv_values(".env.test")
sftp_path = "/data/rdastaging/archive"
local_folder = ".xml_copied"
GNUPG_HOME = '~/.gnupg'

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
    
    for sftp_file in sftp_files:
        local_file_path = os.path.join(local_folder, os.path.basename(sftp_file))
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
            post_url = post_url + "/store/upload_patient_file/overwrite"
            headers = {
                "Content-Type": "application/xml"
            }
            