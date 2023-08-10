"""
Functions to be called in the validation step. 
These will be made available by the api and callable as its own step. This will enable the validity of the xml to be checked prior to any attempt to load and store it (a much more resource heavy process).

Note that the RDA schema versioning is one behind that of the UKRR Dataset
"""


import os
import shutil
from git import Repo  # type: ignore
from lxml import etree  # nosec B410
from pydantic import Field
from pydantic_settings import BaseSettings
from platformdirs import user_data_dir


class Settings(BaseSettings):
    """Load the enviroment variable

    Args:
        BaseSettings (_type_): _description_
    """

    appdata_dir: str = Field(env="APPDATA_DIR", default=user_data_dir())

    # the schema are pinned to specific commits on the resources repo
    schema_repo: str = Field(
        env="SCHEMA_REPO", default="https://github.com/renalreg/resources.git"
    )

    # should be pinned to the highest minor release of version 3 of RDA schema
    v3_commit: str = Field(
        env="V3_COMMIT", default="14fa420a971e16306de3e00cd1fc51b6e344c596"
    )

    # "" version 4 of RDA schema
    v4_commit: str = Field(
        env="V4_COMMIT", default="046b25021c52ebeaff1d878a01aa8ec56c4667ed"
    )


env_variables = Settings()


def download_ukrdc_schema(filepath: str, schema_version: int):
    """
    Downloads the specified schema version from the GitHub repository. A specific commit id is mapped to each supported version of the schema this is loaded via the environment variables.


    Args:
        filepath (str): Directory to download to.
        schema_version (int): Major release number of the schema.

    Note:
        The schema are pinned to specific commits on the resources repo.
    """

    if schema_version == 3:
        commit = env_variables.v3_commit

    elif schema_version == 4:
        commit = env_variables.v4_commit
    else:
        raise ValueError("Unsupported schema version")

    repo_dir = os.path.join(filepath, "temp_files")

    repo = Repo.clone_from(env_variables.schema_repo, repo_dir)
    repo.git.checkout(commit)

    # checkout desired commit, copy schema and clean up
    shutil.copytree(os.path.join(repo_dir, "schema"), os.path.join(filepath, "schema"))
    shutil.rmtree(repo_dir, ignore_errors=True)


def load_schema(schema_version: int):
    """
    Locate the schema locally and load it into lxml so it can be used for validation.

    Args:
        schema_version (int): Major release version of the schema being loaded.

    Returns:
        tuple: Tuple containing the XSD schema and the file path where it's located.

    Raises:
        ValueError: If an unsupported schema version is provided.
    """

    # Load the XSD schema into lxml and if that doesn't work downloading schema files locally from github
    if schema_version == 3:
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
            download_ukrdc_schema(xsd_file_path, 3)
            xsd_doc = etree.parse(
                os.path.join(xsd_file_path, "schema", "ukrdc", "UKRDC.xsd")
            )  # nosec B320

    elif schema_version == 4:
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
            print("downloading missing ukrdc version 4 schema")
            download_ukrdc_schema(xsd_file_path, 4)
            xsd_doc = etree.parse(
                os.path.join(xsd_file_path, "schema", "ukrdc", "UKRDC.xsd")
            )  # nosec B320
    else:
        raise ValueError("Unsupported schema version")

    # This line will break if invalid schema are provided
    # It doesn't see nessary to handle this since the schema should come from our resources repo
    return etree.XMLSchema(xsd_doc), xsd_file_path


def validate_rda_xml_string(rda_xml: str, schema_version: str = "4.0.0"):
    """
    Validate an RDA XML file against the UKRDC schema. It should be noted that the code assumes the enviroment variables are set up such that the minor release can be thrown away. TODO: maybe this is something to be made more explicit or changed in the future.

    Args:
        rda_xml (str): XML file as a string.
        schema_version (str): Version of the dataset to check the XML against (default is 4.0).

    Returns:
        dict or None: If validation fails, returns a dictionary of errors (None if validation passes).
    """

    xml_schema, _ = load_schema(int(schema_version[0]))

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
