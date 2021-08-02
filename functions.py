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

def save_dataset_as_xlsx(data_dict, output_filename, sheetname = 'Sheet1'):
    df = pd.DataFrame(data_dict)
    if os.path.exists(output_filename+".xlsx"):
        book = load_workbook(output_filename+".xlsx")
        writer = pd.ExcelWriter(output_filename+".xlsx", mode="a")
        df.to_excel(writer, sheetname)
        
        writer.save()    
        book.close()

    else:
        if sheetname == 'Sheet1':
            df.to_excel(output_filename+".xlsx")
        else:
            df.to_excel(output_filename+".xlsx", sheet_name = sheetname)

def save_to_sql(data1, table_name):
    df = pd.DataFrame(data1)

    DATABASE_TYPE = 'postgresql'
    DBAPI = 'psycopg2'
    HOST = 'localhost'
    USER = 'postgres'
    PASSWORD = 'password'
    DATABASE = 'Pagila'
    PORT = 5432

    engine = create_engine(f"{DATABASE_TYPE}+{DBAPI}://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}")
    df.to_sql(table_name, engine, if_exists='replace')

class Sources:
    def __init__(self, driver, *args):
        # URLs of the original 4 sources used to build the dataset
        self.source_URL = ["https://www.airliners.net/aircraft-data", "https://www.risingup.com/planespecs/info/", "https://aircraftbluebook.com/Tools/ABB/ShowSpecifications.do", "https://contentzone.eurocontrol.int/aircraftperformance/default.aspx?"]
        self.source_URL.extend(args)
        self.driver = driver

    def data_from_airliners(self):
        self.driver.get(self.source_URL[0])

        # Accept the cookies popup
        self.accept_cookies()

        all_data_sel = self.driver.find_elements_by_class_name("aircraftList")

        data_dict = {'Name' :[], 'Type': [], 'url':[]}

        for div_tags in all_data_sel:
            item2 = div_tags.find_elements_by_tag_name('a')
            if len(item2)>0:
                data_dict['url'].append(item2[0].get_attribute('href'))
            item = div_tags.text.split('\n')
            if len(item)==2:
                data_dict['Name'].append(item[0])

        for link in data_dict['url']:
            sleep(1)
            self.driver.get(link)
            prop_elem = self.driver.find_elements_by_class_name("aircraftProperty")
            for elem in prop_elem:
                if elem.find_element_by_class_name('name').text not in data_dict.keys():
                    data_dict[elem.find_element_by_class_name('name').text] = []
                data_dict[elem.find_element_by_class_name('name').text].append(elem.find_element_by_class_name('description').text)
        
        self.data_airliners = data_dict
        return data_dict

    def accept_cookies(self):
        sleep(2)
        accept_cookies = self.driver.find_element_by_xpath('//*[@id="qc-cmp2-ui"]/div[2]/div/button[2]')

        if accept_cookies.text == 'AGREE':
            relevant_button = accept_cookies
        relevant_button.click()


    def data_from_aircraftbluebook(self):
        self.driver.get(self.source_URL[2])

        data_dict_3 = {'Manufacturer': []}

        # Setting up dictionary keys
        thead = self.driver.find_element_by_tag_name('thead').find_elements_by_tag_name('th')
        for th in thead:
            data_dict_3[th.text] = []

        # Locating the correct table to extract data from
        tbodies = self.driver.find_elements_by_tag_name('table')

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

        self.data_aircraftbluebook = data_dict_3
        return data_dict_3


    def data_from_contentzone(self):
        self.driver.get(self.source_URL[3])

        data_dict_4 = {'Name': [], 'Manufacturer': [], 'Type': [], 'APC': [], 'WPC': [], 'RECAT-EU': [], 'Wing Span': [], 'Length': [], 'Height': [], 'Powerplant': [], 'Wing Position': [], 'Engine Position': [], 'Tail Position': [], 'Landing Gear': [], 'IATA': [], 'Accomodation': [], 'Notes': [], 'Alternative Names': [],}

        id_list = ["MainContent_wsAcftNameLabel", "MainContent_wsManufacturerLabel", "MainContent_wsTypeLabel", "MainContent_wsAPCLabel", "MainContent_wsWTCLabel", "MainContent_wsRecatEULabel", "MainContent_wsLabelWingSpan", "MainContent_wsLabelLength", "MainContent_wsLabelHeight", "MainContent_wsLabelPowerPlant", "MainContent_wsLabelWingPosition", "MainContent_wsLabelEngineData", "MainContent_wsLabelTailPosition", "MainContent_wsLabelLandingGear", "MainContent_wsIATACode", "MainContent_wsLabelAccommodation", "MainContent_wsLabelNotes", "MainContent_wsLabelAlternativeNames"]

        # Step 1: Collect list of aircrafts - total pages -> 39, total results -> 385 
        srch_list = []

        for pg in tqdm(range(2,41)):
            tbody = self.driver.find_element_by_id('MainContent_wsBasicSearchGridView').find_elements_by_tag_name('tr')
            for tr in tbody[3:-2]:
                srch_list.append(tr.find_element_by_tag_name('h3').text)

            td_tags = tbody[0].find_element_by_tag_name('tbody').find_elements_by_tag_name('td')
            for td in td_tags:
                try:
                    if td.find_element_by_tag_name('a').get_attribute('href') == f"javascript:__doPostBack('ctl00$MainContent$wsBasicSearchGridView','Page${pg}')":
                        td.find_element_by_tag_name('a').click()
                        break
                except selenium.common.exceptions.NoSuchElementException:
                    continue # the current page button doesn't have an 'a' tag so I need to ignore that
                except:
                    print("Something else went wrong")
            sleep(1)

        # Step 2: Go over the 385 pages' links
        for i, icao in enumerate(tqdm(srch_list)):
            link = f"https://contentzone.eurocontrol.int/aircraftperformance/details.aspx?ICAO={icao}"
            self.driver.get(link)
            sleep(1)
            for key, id_list_item in zip(data_dict_4.keys(), id_list):
                data_dict_4[key].append(self.driver.find_element_by_id(id_list_item).text)

        self.data_contentzone = data_dict_4
        return data_dict_4
