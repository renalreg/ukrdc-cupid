"""Here we have a quick and dirty script to build a ukrdc db. To be expanded.
"""
from ukrdc_cupid.core.utils import UKRDCConnection
from dotenv import dotenv_values



ENV = dotenv_values(".env.docker")
driver = ENV["UKRDC_DRIVER"]
user = ENV['UKRDC_USER']
password = ENV['UKRDC_PASSWORD']
port = ENV['UKRDC_PORT']
name = ENV['UKRDC_NAME']
host = ENV['UKRDC_HOST']

# generate ukrdc database
#db_url =  f"{driver}://{user}:{password}@db:{port}/{name}"
db_url =  f"{driver}://{user}:{password}@localhost:{port}/{name}"
print(db_url)
connector = UKRDCConnection(url=db_url)
connector.generate_schema(gp_info=True)

print("We have a database :)")

