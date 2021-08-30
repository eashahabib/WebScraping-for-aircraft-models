import functions as fun
import boto3
from datetime import datetime
import os


sources = ['airliners', 'aircraftbluebook', 'contentzone']
data_dict_list = []

# Get data from the sources
data_dict_list.append( fun.Airliners().get_data() )
data_dict_list.append( fun.Aircraftbluebook().get_data() )
data_dict_list.append( fun.Contentzone().get_data() )


# Save the data
for i, source in enumerate(sources):
    fun.save_dataset_as_xlsx(data_dict_list[i], "output", source)
    fun.save_to_sql(data_dict_list[i], source)

# datetime object containing current date and time to upload a unique file everytime
now = datetime.now()
dt_strin = now.strftime("%d%m%Y %H%M%S")

s3_client = boto3.client('s3')
response = s3_client.upload_file("output.xlsx", "web-scraper-project-aircraft", f"output{dt_strin}.xlsx")

# delete the file as its in the s3 bucket anyways
os.remove("output.xlsx")

