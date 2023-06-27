"""
Functions to be called in the validation step. 
These will be made available by the api and callable as its own step. This will enable the validity of the xml to be checked prior to any attempt to load and store it (a much more resource heavy process).
"""


import os
import shutil
from git import Repo  # type: ignore
from lxml import etree  # nosec B410


APPDATA_DIR = os.path.expanduser("~\\AppData\\Local")

# commits to pin the dataset version to
REPO_URL = "https://github.com/renalreg/resources.git"
V3_COMMIT = (
    "f803899cd0a58864347002d63610db2dace11645"  # these xsd schemas currently broken
)
V4_COMMIT = "044b9f25b2d98257cb0cdc11a5fee29d903adc75"
V5_COMMIT = "232d696d3523908be815103a869c9e23b632ce3e"


def download_ukrdc_schema(filepath: str, version: str):
    """Downloads non existant file schema from the github repository

    Args:
        filepath (str): directory to download to
        version (str): version of the dataset
    """

    if version == "v3":
        commit = V3_COMMIT

    if version == "v4":
        commit = V4_COMMIT

    if version == "v5":
        commit = V5_COMMIT

    repo_dir = os.path.join(filepath, "temp_files")
    repo = Repo.clone_from(REPO_URL, repo_dir)

    # checkout desired commit, copy schema and clean up
    repo.git.checkout(commit)
    shutil.copytree(os.path.join(repo_dir, "schema"), os.path.join(filepath, "schema"))
    shutil.rmtree(repo_dir, ignore_errors=True)


def validate_rda_xml_string(rda_xml: str, dataset_version: str):
    """Function to take a RDA xml file and do basic checks against the ukrdc schema

    Args:
        rda_xml (str): xml file as a string
        dataset_version (str): version of the dataset to check the xml against
    """

    # Load the XSD schema and try downloading files if there is an error
    # (I think there are plenty of ways this can break but is should be easily fixable by deleting the folder in APPDATA)
    if dataset_version == "v3":
        try:
            xsd_file_path = os.path.join(APPDATA_DIR, "ukrdc_rda_schema", "v3")
            xsd_doc = etree.parse(
                os.path.join(xsd_file_path, "schema", "ukrdc", "UKRDC.xsd")
            )  # nosec B320
        except OSError:
            print("downloading missing ukrdc version 3 schema")
            download_ukrdc_schema(xsd_file_path, "v3")
            xsd_doc = etree.parse(
                os.path.join(xsd_file_path, "schema", "ukrdc", "UKRDC.xsd")
            )  # nosec B320

    if dataset_version == "v4":
        try:
            xsd_file_path = os.path.join(APPDATA_DIR, "ukrdc_rda_schema", "v4")
            xsd_doc = etree.parse(
                os.path.join(xsd_file_path, "schema", "ukrdc", "UKRDC.xsd")
            )  # nosec B320
        except OSError:
            print("downloading missing ukrdc version 3 schema")
            download_ukrdc_schema(xsd_file_path, "v4")
            xsd_doc = etree.parse(
                os.path.join(xsd_file_path, "schema", "ukrdc", "UKRDC.xsd")
            )  # nosec B320

    if dataset_version == "v5":
        try:
            xsd_file_path = os.path.join(APPDATA_DIR, "ukrdc_rda_schema", "v5")
            xsd_doc = etree.parse(
                os.path.join(xsd_file_path, "schema", "ukrdc", "UKRDC.xsd")
            )  # nosec B320
        except OSError:
            print("downloading missing ukrdc version 3 schema")
            download_ukrdc_schema(xsd_file_path, "v5")
            xsd_doc = etree.parse(
                os.path.join(xsd_file_path, "schema", "ukrdc", "UKRDC.xsd")
            )  # nosec B320

    xml_schema = etree.XMLSchema(xsd_doc)

    # Load the XML file
    xml_doc = etree.XML(rda_xml.encode())

    try:
        xml_schema.assertValid(xml_doc)
        # Initially catch errors to allow reporting multiple issues in one file
        return

    except etree.DocumentInvalid:

        # return errors as dictionary
        errors = {}
        ## what reason is there for not just returning the error log
        for error in xml_schema.error_log:  # type:ignore
            errors[f"line {error.line}"] = error.message

        return errors
