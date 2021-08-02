import requests
from bs4 import BeautifulSoup
from time import sleep
import pandas as pd
from sqlalchemy import create_engine
from tqdm import tqdm
from selenium import webdriver
import selenium
import os.path

from openpyxl import load_workbook

import functions as fun

# Starting chromedriver session
driver = webdriver.Chrome('chromedriver')

# URLs of the 4 sources used to build the dataset
source_URL = ["https://www.airliners.net/aircraft-data", "https://www.risingup.com/planespecs/info/", "https://aircraftbluebook.com/Tools/ABB/ShowSpecifications.do", "https://contentzone.eurocontrol.int/aircraftperformance/default.aspx?"]

########################################################################################################

# driver.get(source_URL[0])

# # Accept the cookies popup
# fun.accept_cookies(driver)

# all_data_sel = driver.find_elements_by_class_name("aircraftList")

# data_dict = {'Name' :[], 'Type': [], 'url':[]}

# for div_tags in all_data_sel:
#     item2 = div_tags.find_elements_by_tag_name('a')
#     if len(item2)>0:
#         data_dict['url'].append(item2[0].get_attribute('href'))
#     item = div_tags.text.split('\n')
#     if len(item)==2:
#         data_dict['Name'].append(item[0])


# for link in data_dict['url']:
#     sleep(1)
#     driver.get(link)
#     prop_elem = driver.find_elements_by_class_name("aircraftProperty")
#     for elem in prop_elem:
#         if elem.find_element_by_class_name('name').text not in data_dict.keys():
#             data_dict[elem.find_element_by_class_name('name').text] = []
#         data_dict[elem.find_element_by_class_name('name').text].append(elem.find_element_by_class_name('description').text)

# fun.save_dataset_as_xlsx(data_dict, "output", "airliners")

########################################################################################################

# data_dict_2 = {'Name': []}

# for index in tqdm(range(4, 521)):
#     sleep(1)
#     URL = f"https://www.risingup.com/planespecs/info/airplane{index}.shtml"
#     driver.get(URL)

#     #checking if the URL exists
#     if driver.find_element_by_tag_name('h1').text.lower() != 'aircraft performance data':
#         continue

#     # filling in the name
#     name = driver.find_element_by_id('thecontent').find_element_by_tag_name('h2')
#     data_dict_2['Name'].append(name.text.split(' - ')[0] )

#     # filling in the data
#     td_tags = driver.find_element_by_id('thecontent').find_elements_by_tag_name('td')
#     for tag in td_tags:
#         if tag.text != '':
#             temp = tag.text.split(':')
#             if len(temp) == 2:
#                 if temp[0] not in data_dict_2:
#                     data_dict_2[temp[0]] = []
                
#                 data_dict_2[temp[0]].append(temp[1])

## can not save due to data set issues

########################################################################################################
driver.get(source_URL[2])

data_dict_3 = {'Manufacturer': []}

# Setting up dictionary keys
thead = driver.find_element_by_tag_name('thead').find_elements_by_tag_name('th')
for th in thead:
    data_dict_3[th.text] = []

# Locating the correct table to extract data from
tbodies = driver.find_elements_by_tag_name('table')

for element in tbodies:
    if element.get_attribute('class') == "idp-table":
        tbody = element.find_element_by_tag_name('tbody').find_elements_by_tag_name('tr')
        
manufacturer = ''

for index, tr in enumerate(tqdm(tbody)):
    if tr.get_attribute('class')=='header':
        manufacturer = tr.text
        continue

    data_dict_3['Manufacturer'].append(manufacturer)

    td_tags = tr.find_elements_by_tag_name('td')
    for key, td in zip( list(data_dict_3.keys())[1:], td_tags ):
        data_dict_3[key].append(td.text)

fun.save_dataset_as_xlsx(data_dict_3, "output_new", "aircraftbluebook2")

########################################################################################################

# driver.get(source_URL[3])

# data_dict_4 = {'Name': [], 'Manufacturer': [], 'Type': [], 'APC': [], 'WPC': [], 'RECAT-EU': [], 'Wing Span': [], 'Length': [], 'Height': [], 'Powerplant': [], 'Wing Position': [], 'Engine Position': [], 'Tail Position': [], 'Landing Gear': [], 'IATA': [], 'Accomodation': [], 'Notes': [], 'Alternative Names': [],}

# id_list = ["MainContent_wsAcftNameLabel", "MainContent_wsManufacturerLabel", "MainContent_wsTypeLabel", "MainContent_wsAPCLabel", "MainContent_wsWTCLabel", "MainContent_wsRecatEULabel", "MainContent_wsLabelWingSpan", "MainContent_wsLabelLength", "MainContent_wsLabelHeight", "MainContent_wsLabelPowerPlant", "MainContent_wsLabelWingPosition", "MainContent_wsLabelEngineData", "MainContent_wsLabelTailPosition", "MainContent_wsLabelLandingGear", "MainContent_wsIATACode", "MainContent_wsLabelAccommodation", "MainContent_wsLabelNotes", "MainContent_wsLabelAlternativeNames"]

# # Step 1: Collect list of aircrafts - total pages -> 39, total results -> 385 
# srch_list = []

# for pg in tqdm(range(2,41)):
#     tbody = driver.find_element_by_id('MainContent_wsBasicSearchGridView').find_elements_by_tag_name('tr')
#     for tr in tbody[3:-2]:
#         srch_list.append(tr.find_element_by_tag_name('h3').text)

#     td_tags = tbody[0].find_element_by_tag_name('tbody').find_elements_by_tag_name('td')
#     for td in td_tags:
#         try:
#             if td.find_element_by_tag_name('a').get_attribute('href') == f"javascript:__doPostBack('ctl00$MainContent$wsBasicSearchGridView','Page${pg}')":
#                 td.find_element_by_tag_name('a').click()
#                 break
#         except selenium.common.exceptions.NoSuchElementException:
#             continue # the current page button doesn't have an 'a' tag so I need to ignore that
#         except:
#             print("Something else went wrong")
#     sleep(1)

# # Step 2: Go over the 385 pages' links
# for i, icao in enumerate(tqdm(srch_list)):
#     link = f"https://contentzone.eurocontrol.int/aircraftperformance/details.aspx?ICAO={icao}"
#     driver.get(link)
#     sleep(1)
#     for key, id_list_item in zip(data_dict_4.keys(), id_list):
#         data_dict_4[key].append(driver.find_element_by_id(id_list_item).text)

# fun.save_dataset_as_xlsx(data_dict_4, "output", "contentzone")

########################################################################################################

# Ending session and closing the driver
driver.close()