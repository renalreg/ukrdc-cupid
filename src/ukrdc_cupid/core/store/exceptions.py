class SchemaVersionError(Exception):
    """This should be used for any type of error caused by mismatches between
    the schema versions
    """


class DataInsertionError(Exception):
    """This error is raised by a failure to commit changes to database"""


class InsertionBlockedError(Exception):
    """This error means cupid hasn't attempted to insert file and has instead
    raised an investigation and stored file as a string because of an issue
    matching domain patient(s).
    """


class DataLinkageBlockedError(Exception):
    """Cupid has inserted a new record but linking it to other records in the
    ukrdc has failed. An investigation against the file has been stored.
    """
