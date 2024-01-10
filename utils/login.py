from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from utils.selenium import bypass_captcha, create_driver, wait_for


def login_google(driver, email, password):
    #locator = (By.CSS_SELECTOR, '[data-tn-element="login-google-button"]')
    #### Make sure that the login button is avaialble
    #wait_for(driver, *locator,20)
    #print("Google")
    #submit_button = driver.find_element(*locator)
    #submit_button.click()
    try:
        # Assuming the pop-up is the second window
        pop_up_window = driver.window_handles[1]  
        driver.switch_to.window(pop_up_window)
    except:
        pass
    # Email
    submit_button = driver.find_element(By.NAME, "identifier")
    submit_button.send_keys(email)
    submit_button.send_keys(Keys.RETURN)
    
    wait_for(driver,By.NAME, "Passwd")
    # Password
    submit_button = driver.find_element(By.NAME, 'Passwd')
    
    by = By.CSS_SELECTOR
    value = "[type = 'password']"
    wait_for(driver, by, value, 15)
    
    submit_button = driver.find_element(by, value)
    submit_button.send_keys(password)
    submit_button.send_keys(Keys.RETURN)
    
    try:
        main_window = driver.window_handles[0]
        driver.switch_to.window(main_window)
    except:
        pass
    driver.implicitly_wait(0.1)
    #driver.switch_to.default_content()

def login_linkedin(driver: Chrome, email, password, google=False):
    url = "https://www.linkedin.com/home"
    driver.get(url)
    
    if google:
        driver.find_element(By.CLASS_NAME,"google-auth-button__placeholder").click()
        login_google(driver,email,password)
    else:
        wait_for(driver, By.ID, "session_key")
        email_input = driver.find_element(By.ID, "session_key")
        email_input.send_keys(email)
        email_input.send_keys(Keys.ENTER)
        
        wait_for(driver, By.ID, "session_password")
        password_input = driver.find_element(By.ID, "session_password")
        password_input.send_keys(password)
        password_input.send_keys(Keys.ENTER)
    
    return driver

def login_glassdoor(driver, email, password, undetected=False, google=False):
    # Set up the Chrome driver (you can use other drivers as well)
    if driver is None:
        driver = create_driver(undetected=undetected) 
    
    if google:
        driver.find_element(By.CLASS_NAME,"google gd-btn ").click()
        login_google(driver,email,password)
    else:
        driver.get("https://www.glassdoor.fr/index.htm")
        sign_in_button = driver.find_element(By.ID, "SignInButton")
        sign_in_button.click()

        wait_for(driver, By.ID, "modalUserEmail")
        email_input = driver.find_element(By.ID, "modalUserEmail")
        email_input.send_keys(email)
        email_input.send_keys(Keys.ENTER)
        
        wait_for(driver, By.ID, "modalUserPassword")
        password_input = driver.find_element(By.ID, "modalUserPassword")
        password_input.send_keys(password)
        password_input.send_keys(Keys.ENTER)
        
        driver.get("https://www.glassdoor.fr/Avis/index.htm")
        
    return driver
    
def check_phone_popup(driver):
    # Verify if there is a phone popup
    print(1)
    driver.window_handles
    print(2)
    if len(driver.window_handles) >= 3:
        print("window handles >= 3", len(driver.window_handles))
    # Back to main page
    main_window = driver.window_handles[0]
    driver.switch_to.window(main_window)
    
    return len(driver.window_handles) >= 3
    
def login_indeed(driver:Chrome, email:str, password:str):
    email_input = driver.find_element(By.NAME, '__email')
    email_input.send_keys(email)
    email_input.send_keys(Keys.RETURN)
    bypass_captcha(driver, method="hcaptcha")

    wait_for(driver, By.NAME, "__password", 15)
    password_input = driver.find_element(By.NAME, '__password')
    password_input.send_keys(password)
    bypass_captcha(driver, method="hcaptcha")
    password_input.send_keys(Keys.RETURN)
    
    
    
    
    
    

