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
from typing import Tuple, Optional, Dict


class Settings(BaseSettings):
    """Load the enviroment variable

    Args:
        BaseSettings (_type_): _description_
    """

    appdata_dir: str = Field(env="APPDATA_DIR", default=user_data_dir())

    schema_repo: str = Field(
        env="SCHEMA_REPO", default="https://github.com/renalreg/resources.git"
    )

    v3_3_0_commit: str = Field(
        env="V3_3_0_COMMIT", default="7095add5ea07369dedbd499fa4662f3f72754d31"
    )

    v3_4_5_commit: str = Field(
        env="V3_4_5_COMMIT", default="14fa420a971e16306de3e00cd1fc51b6e344c596"
    )

    v4_0_0_commit: str = Field(
        env="V4_0_0_COMMIT", default="046b25021c52ebeaff1d878a01aa8ec56c4667ed"
    )


env_variables = Settings()

SUPPORTED_VERSIONS = ["3.3.0", "3.4.5", "4.0.0"]


def download_ukrdc_schema(filepath: str, schema_version: str) -> None:
    """
    Downloads the specified schema version from the GitHub repository. A specific commit id is mapped to each supported version of the schema this is loaded via the environment variables.


    Args:
        filepath (str): Directory to download to.
        schema_version (int): Major release number of the schema.

    Note:
        The schema are pinned to specific commits on the resources repo.
    """

    if schema_version in SUPPORTED_VERSIONS:
        version = "v" + schema_version.replace(".", "_")
        commit = getattr(env_variables, f"{version}_commit")
    else:
        raise ValueError("Unsupported schema version {schema_version}")

    print(commit)

    repo_dir = os.path.join(filepath, "temp_files")

    repo = Repo.clone_from(env_variables.schema_repo, repo_dir)
    repo.git.checkout(commit)

    # checkout desired commit, copy schema and clean up
    shutil.copytree(os.path.join(repo_dir, "schema"), os.path.join(filepath, "schema"))
    shutil.rmtree(repo_dir, ignore_errors=True)


def load_schema(schema_version: str) -> Tuple[etree.XMLSchema, str]:
    """
    Locate the schema locally and load it into lxml so it can be used for validation.

    Args:
        schema_version (int): Major release version of the schema being loaded.

    Returns:
        tuple: Tuple containing the XSD schema and the file path where it's located.

    Raises:
        ValueError: If an unsupported schema version is provided.
    """

    # assemble the information required to load locally stored xsd schema and complain if unsupported version is used
    if schema_version in SUPPORTED_VERSIONS:
        formatted_ver = schema_version.replace(".", "_")
        commit = getattr(env_variables, f"v{formatted_ver}_commit")
    else:
        raise ValueError("Unsupported schema version {schema_version}")

    xsd_file_path = os.path.join(
        env_variables.appdata_dir,
        "ukrdc_rda_schema",
        "v" + formatted_ver,
        commit,
    )
    ukrdc_path = os.path.join(xsd_file_path, "schema", "ukrdc", "UKRDC.xsd")

    try:
        xsd_doc = etree.parse(ukrdc_path)  # nosec B320
    except OSError:
        download_ukrdc_schema(xsd_file_path, schema_version=schema_version)
        xsd_doc = etree.parse(ukrdc_path)  # nosec B320

    return etree.XMLSchema(xsd_doc), xsd_file_path


def validate_rda_xml_string(
    rda_xml: str, schema_version: str = "4.0.0"
) -> Optional[Dict[str, str]]:
    """
    Validate an RDA XML file against the UKRDC schema. It should be noted that the code assumes the enviroment variables are set up such that the minor release can be thrown away. TODO: maybe this is something to be made more explicit or changed in the future.

    Args:
        rda_xml (str): XML file as a string.
        schema_version (str): Version of the dataset to check the XML against (default is 4.0).

    Returns:
        dict or None: If validation fails, returns a dictionary of errors (None if validation passes).
    """

    xml_schema, _ = load_schema(schema_version)

    # Load the XML file
    xml_doc = etree.XML(rda_xml.encode())

    # Initially catch errors to allow more specific processing of errors
    try:
        xml_schema.assertValid(xml_doc)

    except etree.DocumentInvalid:

        # return errors as dictionary
        errors = {}
        ## what reason is there for not just returning the error log
        for error in xml_schema.error_log:  # type:ignore
            errors[f"line {error.line}"] = error.message

        return errors
