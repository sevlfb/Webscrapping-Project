from utils.login import login_linkedin
from utils.selenium import create_driver

def enter_parameters(driver, job_title, location):
        
    linkedin_job_list_url = "https://www.linkedin.com/jobs/search/?keywords={job_title}&location={location}&origin=BLENDED_SEARCH_RESULT_CARD_NAVIGATION"
    
    driver.get(linkedin_job_list_url.format(job=job_title,location=location))
    
    return driver

def setup_linkedin(driver, email, password, undetected=False, google=False): # login indeed from scratch
    # Set up the Chrome driver (you can use other drivers as well)
    if driver is None:
        driver = create_driver(undetected=undetected) 

    driver = login_linkedin(driver, email, password, google=google)
    return driver