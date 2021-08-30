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

from dataclasses import dataclass



def save_dataset_as_xlsx(data_dict, output_filename, sheetname = 'Sheet1'):
    """The function saves the file ton an xlsx file in the current directory. 
    
    Parameters: 
    data_dict (dict): dictionary of the data to be stored in the excel file
    output_filename (str): name of the excel file, without the file extension
    sheetname (str): name for the excel sheet
    
    Returns:
    None (the data is stored in a excel file which should be visible in the folder) 
    """


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
    """The function saves the file to an sql database i.e. 
    DATABASE_TYPE = 'postgresql'
    DBAPI = 'psycopg2'
    HOST = 'localhost'
    USER = 'postgres'
    PASSWORD = 'password'
    DATABASE = 'Pagila'
    PORT = 5432 
    
    Parameters: 
    data1 (dict): dictionary of the data to be stored in the SQL table
    table_name (str): name of the SQL table
    
    Returns:
    None (the data is stored in the SQL table which should be visible in the database) 
    """
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


def set_up_Chrome(URL):
    print('Opening Chrome...')
    driver = webdriver.Chrome('chromedriver')
    
    print('Opening source URL...')
    driver.get(URL)

    return driver


@dataclass
class Sources:
    """The class contains information about sources and the data scraped from them. 

    - Parent class for the source calls. 
    - Helps keeps a consistent style across all the classes
    
    """
    driver: selenium.webdriver.chrome.webdriver.WebDriver
    data_dict: dict

    def __init__(self):
        pass

    def get_data(self):
        pass

    def housekeeping(self):
        self.driver.quit()


@dataclass
class Airliners(Sources):

    def __init__(self):
        source_URL = "https://www.airliners.net/aircraft-data"
        self.driver = set_up_Chrome(source_URL)

    def get_data(self):
        """Scrapes data from airliners.net

        Parameters:
        self

        Returns:
        data_dict (dict): dictionary of data scraped from the corresponding source

        """

        # Accept the cookies popup
        self.accept_cookies()

        self.get_urls()

        self.mine_data()

        self.housekeeping()
        
        return self.data_dict


    def mine_data(self):
        for link in self.data_dict['url']:
            sleep(1)
            self.driver.get(link)
            prop_elem = self.driver.find_elements_by_class_name("aircraftProperty")
            for elem in prop_elem:
                self.check_keys(elem)
                self.data_dict[elem.find_element_by_class_name('name').text].append(elem.find_element_by_class_name('description').text)


    def get_urls(self):
        
        all_data_sel = self.driver.find_elements_by_class_name("aircraftList")

        self.data_dict = {'Name' :[], 'url':[]}

        for div_tags in all_data_sel:
            item2 = div_tags.find_elements_by_tag_name('a')
            if len(item2)>0:
                self.data_dict['url'].append(item2[0].get_attribute('href'))
            item = div_tags.text.split('\n')
            if len(item)==2:
                self.data_dict['Name'].append(item[0])

    def check_keys(self, elem):
        if elem.find_element_by_class_name('name').text not in self.data_dict.keys():
            self.data_dict[elem.find_element_by_class_name('name').text] = []
            
    def accept_cookies(self):
        """Accepts cookies for airliners.net

        Parameters:
        self

        Returns:
        None

        """
        
        sleep(2)
        accept_cookies = self.driver.find_element_by_xpath('//*[@id="qc-cmp2-ui"]/div[2]/div/button[2]')

        if accept_cookies.text == 'AGREE':
            relevant_button = accept_cookies
        relevant_button.click()


@dataclass
class Aircraftbluebook(Sources):

    def __init__(self):
        source_URL = "https://aircraftbluebook.com/Tools/ABB/ShowSpecifications.do"
        self.driver = set_up_Chrome(source_URL)


    def get_data(self):
        """Scrapes data from aircraftbluebook

        Parameters:
        self

        Returns:
        data_dict (dict): dictionary of data scraped from the corresponding source

        """
        self.get_keys()

        self.read_table()
        
        self.housekeeping()

        return self.data_dict
        
    def get_keys(self):
        self.data_dict = {'Manufacturer': []}

        # Setting up dictionary keys
        thead = self.driver.find_element_by_tag_name('thead').find_elements_by_tag_name('th')
        for th in thead:
            self.data_dict[th.text] = []

    def get_table_rows(self):
        tbodies = self.driver.find_elements_by_tag_name('table')

        for element in tbodies:
            if element.get_attribute('class') == "idp-table":
                tbody = element.find_element_by_tag_name('tbody').find_elements_by_tag_name('tr')
        
        return tbody

    def read_table(self):
        manufacturer = ''

        for index, tr in enumerate(tqdm(self.get_table_rows())):
            if tr.get_attribute('class')=='header':
                manufacturer = tr.text
                continue

            self.data_dict['Manufacturer'].append(manufacturer)

            td_tags = tr.find_elements_by_tag_name('td')
            for key, td in zip( list(self.data_dict.keys())[1:], td_tags ):
                self.data_dict[key].append(td.text)


@dataclass
class Contentzone(Sources):
    def __init__(self):
        self.source_URL = "https://contentzone.eurocontrol.int/aircraftperformance/default.aspx?"
        self.driver = set_up_Chrome(self.source_URL)
        self.driver.fullscreen_window()

    def get_data(self):
        """Scrapes data from contentzone

        Parameters:
        self

        Returns:
        data_dict (dict): dictionary of data scraped from the corresponding source

        """
        self.set_keys_ids()

        # Step 1: Collect list of aircrafts - total pages -> 39, total results -> 385 
        self.get_plane_codes()

        # Step 2: Go over the 385 pages' links
        self.mine_data()

        return self.data_dict

    def get_keys(self):
        self.data_dict = {'ICAO': [], 'Name': [], 'Manufacturer': [], 'Type': [], 'APC': [], 'WPC': [], 'RECAT-EU': [], 'Wing Span': [], 'Length': [], 'Height': [], 'Powerplant': [], 'Wing Position': [], 'Engine Position': [], 'Tail Position': [], 'Landing Gear': [], 'IATA': [], 'Accomodation': [], 'Notes': [], 'Alternative Names': []}
        self.id_list = ["MainContent_wsAcftNameLabel", "MainContent_wsManufacturerLabel", "MainContent_wsTypeLabel", "MainContent_wsAPCLabel", "MainContent_wsWTCLabel", "MainContent_wsRecatEULabel", "MainContent_wsLabelWingSpan", "MainContent_wsLabelLength", "MainContent_wsLabelHeight", "MainContent_wsLabelPowerPlant", "MainContent_wsLabelWingPosition", "MainContent_wsLabelEngineData", "MainContent_wsLabelTailPosition", "MainContent_wsLabelLandingGear", "MainContent_wsIATACode", "MainContent_wsLabelAccommodation", "MainContent_wsLabelNotes", "MainContent_wsLabelAlternativeNames"]

    def get_plane_codes(self):
        # FIXME: the range should be dynamic, rather than fixed
        for pg in tqdm(range(2,41)):
            tbody_0 = self.explore_page()

            self.next_page(tbody_0)


    def explore_page(self):
        tbody = self.driver.find_element_by_id('MainContent_wsBasicSearchGridView').find_elements_by_tag_name('tr')

        for tr in tbody[3:-2]:
            self.data_dict['ICAO'].append(tr.find_element_by_tag_name('h3').text)

        return tbody[0]

    def next_page(tbody_pos):
        td_tags = tbody_pos.find_element_by_tag_name('tbody').find_elements_by_tag_name('td')
            
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

    def mine_data(self):
        for i, icao in enumerate(tqdm(self.data_dict['ICAO'])):
            link = self.source_URL+f"ICAO={icao}"
            self.driver.get(link)
            sleep(1)
            for key, id_list_item in zip(self.data_dict.keys(), self.id_list):
                self.data_dict[key].append(self.driver.find_element_by_id(id_list_item).text)
