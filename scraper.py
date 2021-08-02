from selenium import webdriver
import functions as fun

# Starting chromedriver session
driver = webdriver.Chrome('chromedriver')

#creating an instance of the class with the data collection methods
data_collector = fun.Sources(driver)

########################################################################################################
data_dict_1 = data_collector.data_from_airliners()

fun.save_dataset_as_xlsx(data_dict_1, "output", "airliners")
fun.save_to_sql(data_dict_1, "airliners")

########################################################################################################
data_dict_2 = data_collector.data_from_aircraftbluebook()

fun.save_dataset_as_xlsx(data_dict_2, "output", "aircraftbluebook")
fun.save_to_sql(data_dict_2, "aircraftbluebook")

########################################################################################################
data_dict_3 = data_collector.data_from_contentzone()

fun.save_dataset_as_xlsx(data_dict_3, "output", "contentzone")
fun.save_to_sql(data_dict_3, "contentzone")

########################################################################################################

# Ending session and closing the driver
driver.close()