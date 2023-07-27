"""
Functions to be called in the validation step. 
These will be made available by the api and callable as its own step. This will enable the validity of the xml to be checked prior to any attempt to load and store it (a much more resource heavy process).
"""


import os
import shutil
from git import Repo  # type: ignore
from lxml import etree  # nosec B410
from pydantic import Field
from pydantic_settings import BaseSettings
from platformdirs import user_data_dir


class Settings(BaseSettings):
    appdata_dir: str = Field(env="APPDATA_DIR", default=user_data_dir())
    schema_repo: str = Field(
        env="SCHEMA_REPO", default="https://github.com/renalreg/resources.git"
    )
    v3_commit: str = Field(
        env="V3_COMMIT", default="232d696d3523908be815103a869c9e23b632ce3e"
    )
    v4_commit: str = Field(
        env="V4_COMMIT", default="044b9f25b2d98257cb0cdc11a5fee29d903adc75"
    )
    v5_commit: str = Field(
        env="V5_COMMIT", default="232d696d3523908be815103a869c9e23b632ce3e"
    )


env_variables = Settings()


def download_ukrdc_schema(filepath: str, version: str):
    """Downloads non existant file schema from the github repository

    Args:
        filepath (str): directory to download to
        version (str): version of the dataset
    """

    if version == "v3":
        commit = env_variables.v3_commit

    if version == "v4":
        commit = env_variables.v4_commit

    if version == "v5":
        commit = env_variables.v5_commit

    repo_dir = os.path.join(filepath, "temp_files")

    repo = Repo.clone_from(env_variables.schema_repo, repo_dir)

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
            xsd_file_path = os.path.join(
                env_variables.appdata_dir,
                "ukrdc_rda_schema",
                "v3",
                env_variables.v3_commit,
            )
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
            xsd_file_path = os.path.join(
                env_variables.appdata_dir,
                "ukrdc_rda_schema",
                "v4",
                env_variables.v4_commit,
            )
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
            xsd_file_path = os.path.join(
                env_variables.appdata_dir,
                "ukrdc_rda_schema",
                "v5",
                env_variables.v3_commit,
            )
            xsd_doc = etree.parse(
                os.path.join(xsd_file_path, "schema", "ukrdc", "UKRDC.xsd")
            )  # nosec B320
        except OSError:
            print("downloading missing ukrdc version 3 schema")
            download_ukrdc_schema(xsd_file_path, "v5")
            xsd_doc = etree.parse(
                os.path.join(xsd_file_path, "schema", "ukrdc", "UKRDC.xsd")
            )  # nosec B320

    # This line will break if invalid schema are provided
    # It doesn't see nessary to handle this since the schema should come from our resources repo
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
