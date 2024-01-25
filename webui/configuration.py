import os


def getEnvironmentalConfigurationForMySQLServer():
    """
    Get shit from os.environ
    :rtype: dict
    """
    return {
        "host": os.getenv("MYSQL_HOST"),
        "user": os.getenv("MYSQL_USER"),
        "password": os.getenv("MYSQL_PASSWORD"),
        "database": os.getenv("MYSQL_DATABASE")
    }