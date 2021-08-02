import requests
from bs4 import BeautifulSoup
from time import sleep
import pandas as pd
from sqlalchemy import create_engine
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import os.path

from openpyxl import load_workbook

def accept_cookies(driver):
    sleep(2)
    accept_cookies = driver.find_element_by_xpath('//*[@id="qc-cmp2-ui"]/div[2]/div/button[2]')

    if accept_cookies.text == 'AGREE':
        relevant_button = accept_cookies
    relevant_button.click()


def save_dataset_as_xlsx(data_dict, output_filename, sheetname = 'Sheet1'):
    df = pd.DataFrame(data_dict)
    if os.path.exists(output_filename+".xlsx"):
        book = load_workbook(output_filename+".xlsx")
        writer = pd.ExcelWriter(output_filename+".xlsx", mode="a")
        df.to_excel(writer, sheetname)
        writer.save()
        print()
        print("here here")
        print()
        # if sheetname not in book.sheetnames:
            
        book.close()

    else:
        if sheetname == 'Sheet1':
            df.to_excel(output_filename+".xlsx")
        else:
            df.to_excel(output_filename+".xlsx", sheet_name = sheetname)