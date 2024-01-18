import time

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


# Permet d'attendre qu'un élément s'affiche sans changer le "implicitly_wait" time
def wait_for(driver, by, value, max_time=10, verbose=False):
    iframe_locator = (by, value)
    #WebDriverWait(driver, max_time).until(EC.presence_of_element_located(iframe_locator))
    try:
        WebDriverWait(driver, max_time).until(EC.element_to_be_clickable(iframe_locator))
        return True
    except:
        try:
            pop_up_window = driver.window_handles[1]  
            driver.switch_to.window(pop_up_window)
            WebDriverWait(driver, max_time).until(EC.element_to_be_clickable(iframe_locator))
            if verbose: print("pop-up switch")
            return True
        except:
            if verbose: print(f"Not Found : {value}")
            return False
        
# Permet simplement de vérifier rapidement si un élément est présent sur la page.
def element_exists(driver, by, value):
    try:
        driver.find_element(by, value)
        return True
    except NoSuchElementException:
        return False
    except Exception as e:
        print(e)
        return False
  
   
def create_driver(undetected=False):
    options = webdriver.ChromeOptions()
    #options.add_argument("--headless")
    #options.add_argument("--blink-settings=imagesEnabled=false")
    #options.add_argument("--disable-infobars")
    options.add_argument("--disable-notifications")
    #options.add_argument("--headless")
    options.add_argument("--window-size=1920,1080")
    #options.add_argument("--window-size=800,800")
    #options.add_argument("--auto-open-devtools-for-tabs")
    #options.add_argument("--disable-gpu")
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--allow-running-insecure-content')
    #options.add_argument('--profile-directory=' + str(int(time.time())))
    #user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
    #options.add_argument(f'user-agent={user_agent}')
    #CHROME_VERSION = "121.0.6167.14"
    #dir = 'C:\\Users\\sever\\AppData\\Roaming\\undetected_chromedriver\\undetected\\chromedriver-win32\\chromedriver.exe'
    #dir = r'C:\\Users\\sever\\AppData\\Roaming\\undetected_chromedriver\\undetected\\chromedriver-win32\\chromedriver.exe'
    #if undetected:
    #    print("undetected activated yes !!!!")
    #    driver = Driver.Chrome(uc=True, options=options)
    #else:
    driver = webdriver.Chrome(options=options)
     
    driver.implicitly_wait(0.1)
    #driver.set_window_position(2000,2000)
    return driver
  
    
def bypass_captcha(driver, method):
    if method.lower() == "cloudflare": bypass_cloudflare_captcha(driver)
    if method.lower() == "hcaptcha": bypass_hcaptcha(driver) 

# If return True -> we quit
def bypass_cloudflare_captcha(driver, quit_=True):
    #by = By.TAG_NAME
    #value = "iframe"
    by = By.ID
    value = "challenge-stage"
    if len(driver.find_elements(by,value))>0:
        print("##### CAPTCHA PAGE ######")
        page_source = driver.page_source
        with open("page_source_pre.txt","w") as f:
            f.write(page_source)
        l = (By.PARTIAL_LINK_TEXT, "#challenge-stage > div > label > span.ctp-label")
        l=(By.XPATH, '//*[@id="challenge-stage"]/div/label')
        l = (By.TAG_NAME, 'iframe')
        #l = (By.TAG_NAME, 'input')
        #l = (By.NAME, "cf-turnstile-response")
        if wait_for(driver,*l,30):
            print("##### CAPTCHA FOUND ON THE PAGE #####")
            if quit_:
                print("#QUIT#")
                return True
            time.sleep(5)
        else:
            print("##### CAPTCHA NOT DETECTED ######")
        page_source = driver.page_source
        with open("page_source_post.txt","w") as f:
            f.write(page_source)
        return _bypass_captcha(driver, *l)
         
            
def bypass_hcaptcha(driver):
    driver.switch_to.default_content()
    by = By.TAG_NAME
    value = 'iframe'
    captcha_frame = driver.find_elements(by, value)
    frame_to = len(captcha_frame)
    print(captcha_frame)
    #value = 'form'
    #captcha_frame = driver.find_elements(by, value)
    #print(captcha_frame)
    #driver.switch_to.frame(captcha_frame[4].get_attribute("xpath"))
    driver.switch_to.frame(frame_to-2)
    #checkbox
    by = By.TAG_NAME
    value = 'div'
    ##driver.switch_to.default_content()
    captcha_frame = driver.find_elements(by, value)
    print(captcha_frame)
    for c in captcha_frame:
        if c.get_attribute("id") == "checkbox":
            print("yeeeeeeees")
            c.click()
            break
    #//*[@id="checkbox"]
    #emailform > div.pass-Captcha.css-pflzf3.eu4oa1w0 > div > iframe
    #//*[@id="emailform"]/div[2]/div/iframe
    driver.switch_to.default_content()
    ##switch to new frame again:
    by = By.TAG_NAME
    value = 'iframe'
    captcha_frame = driver.find_elements(by, value)
    frame_to = len(captcha_frame)
    print(frame_to)
    driver.switch_to.frame(1)
    by = By.CLASS_NAME
    value = 'hcaptcha-logo'
    ##driver.switch_to.default_content()
    captcha_frame = driver.find_elements(by, value)
    print(driver)
    if len(captcha_frame) > 0 : print("yeeeees")
    #time.sleep(1)
    #if _bypass_captcha(driver, by, value):
    hcaptcha_solution(driver)

def hcaptcha_solution(driver):
    time.sleep(3)
    recaptcha_solution = driver.execute_script("document.getElementById('h-recaptcha-response').style = 'width: 250px; height: 40px; border: 1px solid rgb(193, 193, 193); margin: 10px 25px; padding: 0px;';")    
    time.sleep(3)
    driver.find_element(By.XPATH,'//*[@id="h-recaptcha-response"]').send_keys(recaptcha_solution)
    
def _bypass_captcha(driver, by, value):
    wait_for(driver, by, value, 0.1) #maybe never put it
    if element_exists(driver, by, value):
        #print("")
        checkbox_locator = (by, value)
        
        #### Loop method
        
        #poll_rate = 1
        #current_url = driver.current_url
        #while driver.current_url == current_url:
        #    time.sleep(poll_rate)
        
        #### Trying to click #### currently impossible
        
        try:
            # Wait for the cpatcha to appear and be clickable
            WebDriverWait(driver, 30).until(EC.element_to_be_clickable(checkbox_locator)).click()
        except:
            driver.find_element(by, value).click()
        return True
            
    else:
        print("no captcha found")
        return False