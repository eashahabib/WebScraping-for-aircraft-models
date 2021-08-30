import functions as fun

sources = ['airliners', 'aircraftbluebook', 'contentzone']
data_dict = []

# Get data from the sources
data_dict[0] = fun.Airliners().get_data()
data_dict[1] = fun.Aircraftbluebook().get_data()
data_dict[2] = fun.Contentzone().get_data()

# Save the data
for i, source in enumerate(sources):
    fun.save_dataset_as_xlsx(data_dict[i], "output", source)
    fun.save_to_sql(data_dict[i], source)


