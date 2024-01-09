from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from utils.selenium import bypass_captcha, wait_for
from utils.login import login_google, login_indeed, login_linkedin
from utils.threading import init_drivers, force_patcher_to_use
import undetected_chromedriver as ucw
import os
import shutil
import tempfile
from utils.selenium import create_driver

def enter_parameters(driver, job_title, location):
        
    linkedin_job_list_url = "https://www.linkedin.com/jobs/search/?keywords={job_title}&location={location}&origin=BLENDED_SEARCH_RESULT_CARD_NAVIGATION"
    
    driver.get(linkedin_job_list_url.format(job=job_title,location=location))
    
    return driver

def setup_linkedin(driver, email, password, undetected=False, google=False): # login indeed from scratch
    # Set up the Chrome driver (you can use other drivers as well)
    if driver is None:
        print("Creating driver")
        driver = create_driver(undetected=undetected) 

    driver = login_linkedin(driver, email, password, google=google)
    return driver