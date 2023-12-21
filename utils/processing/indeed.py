from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from utils.selenium import bypass_captcha, wait_for
from utils.login import login_google, login_indeed
from utils.threading import init_drivers

def get_indeed_start_page(driver):
    t = []
    dfs = []
    for drivers in list_drivers:
        t_indeed = ThreadWithReturnValue(get_job_data(drivers[0], verbose, bypass))
                                        #args=(drivers, verbose, bypass))
        t_indeed.start()
        t.append(t_indeed)
    for i in t:
        dfs.append(t_indeed.join())

def enter_indeed_parameters(driver, job_title, city):
    # Voir avec urllib !!!
    wait_for(driver, By.NAME, "q")
    job_title_input = driver.find_element(By.NAME, "q")
    job_title_input.clear()
    time.sleep(0.1)
    job_title_input.send_keys(job_title)
    #job_title_input.send_keys(Keys.RETURN)

    #input_locator = (By.NAME, "l")
    location_input = driver.find_element(By.NAME, "l")
    #location_input.__setattr__("value","Paris")
    #input_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located(input_locator))
    location_input.click()
    #wait_for(driver, By.CSS_SELECTOR, '[aria-label="Clear location input"]')
    try:  
        clear_button = driver.find_element(By.CSS_SELECTOR, '[aria-label="Clear location input"]')
        clear_button.click()
    except:
        try:
            clear_button = driver.find_elements(By.CSS_SELECTOR, '[aria-label="Clear"]')[-1]
            clear_button.click()
        except:
            pass
    location_input.send_keys(city)
    #driver.execute_script("arguments[0].value = arguments[1];", location_input, city)  

    search_button_locator = (By.CSS_SELECTOR, '[type="submit"]')
    #search_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable(search_button_locator))
    #search_button.click()
    try:
        clicker = driver.find_element(By.CSS_SELECTOR, '[type="submit"]')
        clicker.click()
    except:
        location_input.send_keys(Keys.RETURN)
        
    # Close the popup
    if wait_for(driver, By.CSS_SELECTOR, '[aria-label="fermer"]', 2):
        in_page_popup = driver.find_element(By.CSS_SELECTOR, '[aria-label="fermer"]')
        in_page_popup.click()
    
    # id="filter-dateposted"
    # driver.find element (tag, a)
    # Dates : fromage=
    
    #id="filter-srctype"
    
    return driver

def pre_login(url=""):
    # Set up the Chrome driver (you can use other drivers as well)
    options = webdriver.ChromeOptions()
    #options.add_argument("--headless")
    options.add_argument("--blink-settings=imagesEnabled=false")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-notifications")
    #options.add_argument("--headless")
    #options.add_argument("--window-size=1920,1080")
    options.add_argument("--window-size=800,800")
    options.add_argument("--disable-gpu")
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--allow-running-insecure-content')
    #user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
    #options.add_argument(f'user-agent={user_agent}')
    driver = webdriver.Chrome(options=options)
    #driver.set_window_position(2000,2000)
    driver.implicitly_wait(0.01)
    #Indeed Login
    driver.get("https://fr.indeed.com/?from=jobsearch-empty-whatwhere")
    print(driver)
    bypass_captcha(driver, method="cloudlfare")
    print(driver)
   # Button for login
   #'[data-gnav-element-name="SignIn"]'
   #'//*[@id="gnav-main-container"]/div/div/div[2]/div[2]/div[3]/div/a'
    wait_for(driver, By.CSS_SELECTOR, '[data-gnav-element-name="SignIn"]', 1, verbose=True)
    button = driver.find_element(By.CSS_SELECTOR, '[data-gnav-element-name="SignIn"]')
    button.click()
    return driver

def login_indeed_from_scratch(email, password):
    driver = pre_login()
    driver = login_google(driver, email, password)
    return driver

def setup_indeed(job_title, city, email, password): # login indeed from scratch
    url = ""
    driver = pre_login(url)
    
    login_google(driver, email, password)
    #login_indeed(driver, email, password)
    
    driver = enter_indeed_parameters(driver, job_title, city)
    return driver