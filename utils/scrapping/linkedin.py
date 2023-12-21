from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup
import requests
from utils.selenium import bypass_captcha, wait_for, element_exists
import urllib
from selenium import webdriver
from utils.login import login_google
import pandas as pd
from utils.threading import ThreadWithReturnValue
import numpy as np
import regex as re
from utils.scrapping.eco_score import get_eco_score
from utils.scrapping.glassdoor import get_company_info
from selenium.webdriver.common.action_chains import ActionChains


def loop_pages(list_drivers, verbose, bypass):
    t = []
    dfs = []
    for drivers in list_drivers:
        t_indeed = ThreadWithReturnValue(target = get_job_data,
                                         args=(drivers, verbose, bypass))
                                        #args=(drivers, verbose, bypass))
        t_indeed.start()
        t.append(t_indeed)
    for i in t:
        dfs.append(i.join())
    return dfs

def get_filters(driver):
    filters_dict = dict()
    try:
        filters_names = driver.find_elements(By.CLASS_NAME, "yosegi-FilterPill-dropdownPillContainer")
    except:
        filters_names = list()
    #print(len(filters_names))
    for filter in filters_names:
        #print("====== Filter =====")
        filter_title = filter.find_element(By.CLASS_NAME, "yosegi-FilterPill-pillLabel").text
        #### Handle default "25km" of Location
        if filter_title[-2:] == "km" : filter_title = "Emplacement"
        #print("Filter =", filter_title)
        filter.click()
        els_ = filter.find_elements(By.TAG_NAME, "a")
        filters_attrs = []
        #print("Filter objects")
        for e in els_:
            h = e.get_attribute("href")
            if h.count("&") == 0:
                h = ""
            if filter_title == "Salaire":
                h = h.split("&")[0].split("+")[-2]+"+€"
                #print(h)
            else:
                h = h.split("&")[-1]
            #### sc=0kf%3A ... %3B
            if h[:2] == "sc":
                h = "sc::"+h[9:-3]+"%%%%"
            if "radius" not in h and filter == "radius":
                h = "radius=" + re.search(r'\d+', e.text).group()
            #print(e.text, h)
            filters_attrs.append((e.text,h))
        filters_dict[filter_title] = filters_attrs
        
    for filter, values in filters_dict.items():
        temp = [(filter,'')] + values
        seen = set()
        filters_dict[filter] = [x for x in temp if not (x in seen or seen.add(x))]
        filters_dict[filter] = dict(zip([x[0] for x in temp], [x[1] for x in temp]))
        
    return filters_dict


def scrap_job_info(layout, verbose=False, bypass=False):
    print("scrap job info")
    deb = time.time()
    
    #Title
    job_title = layout.find_element(By.CLASS_NAME,"job-details-jobs-unified-top-card__job-title-link").text
    
    job_block = layout.find_element(By.CLASS_NAME,"job-details-jobs-unified-top-card__primary-description-container")
    
    
    #### Launch this thread
    try:
        text_to_treat = job_block.find_element(By.CSS_SELECTOR,'div:nth-child(1)').text
        list_of_spans = [e.text for e in job_block.find_elements(By.TAG_NAME,"span")] #+ [company]
        for span in list_of_spans:
            text_to_treat = text_to_treat.replace(span.strip(),"")
        loc_desc = [x.strip() for x in text_to_treat.strip().split(",")]
        loc_tags = ["Ville", "Région", "Pays"]
        loc_ = dict(zip(loc_tags,loc_desc))
        #print("cc",company, "test",loc_,"fin", "",sep="\n")
        job_details = layout.find_elements(By.CLASS_NAME, "job-details-jobs-unified-top-card__job-insight")
        job_tags = []
        for detail in job_details:
            try:
                job_tags.append(detail.text)
            except:
                job_tags.append('')      
    except:
        job_tags = []
    
    #print("RESULT INFO !!!!!!!!!!!!", len(result_info))
    #print("result_info", result_info)
    
    if verbose:
        print("**Time of scrapping job infos**:", time.time()-deb)
    
    print("job_tags", job_tags)
    
    return job_tags


def get_job_data(drivers, job, location, verbose=True, limit: int=None, bypass=True):
    print("get job data")
    # Max time for checking element. Lower = Faster
    #driver.implicitly_wait(0.1)
    
    main_driver = drivers[0]
    glassdoor_drivers = drivers[1:4]
    glassdoor_drivers[0].get("https://www.glassdoor.fr/Avis/index.htm")
    eco_driver = drivers[-1]
    # HTML Item for the job description
    linkedin_jobs_url = f"https://www.linkedin.com/jobs/search/?keywords={job}t&location={location}&origin=BLENDED_SEARCH_RESULT_CARD_NAVIGATION"
    main_driver.get(linkedin_jobs_url)
    time.sleep(1)
    job_elements = main_driver.find_element(By.CLASS_NAME, "scaffold-layout__list-container").find_elements(By.XPATH, "*")
    print(len(job_elements))
    if type(limit) == int: 
        job_elements = job_elements[:limit]
    
    if verbose:
        deb = time.time()
    
    # Captcha kills the loop of research. Captcha appears every 2.5 pages
    try:
        # if no job element -> captcha
        job_title = job_elements[0].find_element(By.TAG_NAME, "span").get_attribute("title") # Title / Entreprise
    except:
        if bypass:
            bypass_captcha(main_driver, method="cloudflare")
            main_driver.back()
            stop = True
    
    if verbose:
        print("**Time of pre-loop Bypass :** ", time.time()-deb)
        
    #if wait_for(lookup_driver, *loca, 1):
    #    button = lookup_driver.find_element(*loca)
    #    button.click()
    
    #Info to get / Columns:
    titles = []
    companies = []
    locations = []
    ids = []
    job_url_list = []
    companies_url = []
    competencies_list = []
    salaries = []
    post_type = []
    hours = []
    CEOs = []
    founded = []
    nb_employees = []
    human_ratings = []
    salary_satisfactions = []
    reviews = []
    company_names, eco_scores = [], []
    addings = [CEOs, founded, nb_employees, human_ratings, salary_satisfactions]
    addings = np.array(addings)
    
    
    # For every job offer on the page  
    for job_element in job_elements:
        print("New_element")
        ### With one job element, we look for :
        # In-page elements -> get job
        # Job_link infos -> get company
        # Company_link infos
        # ^^^^ / reviews infos
        
        ###
        # Function for in page scrapping and list of jobs
        # Function for job scrapping
        # Function for company scrapping
        # Function for review scrapping
        
        # Thread 0 : scrapp all in page data -> instantaneous
        ### Loop through all elements of Thread 0 
        # Thread 1 : job_scrapping function
            # Thread 2 : company scrapping
            # Thread 3 : review scrapping
            ### wait for 1-2-3 to finsish and back to loop
        
        wait_for(main_driver, By.CLASS_NAME, 'job-view-layout.jobs-details', 2)
        # Get the company name
        company = job_element.find_element(By.CLASS_NAME,"job-card-container__primary-description").text
        
        ##### Glassdoor thread
        print("company:",company)
        
        thread_company = ThreadWithReturnValue(target=get_company_info, 
                                            args=(glassdoor_drivers, company, verbose, bypass))
        thread_company.start()
        
        
        ##### Job Thread
        hover = ActionChains(main_driver).move_to_element(job_element).click()
        print(job_element)
        hover.perform()
        wait_for(main_driver, By.CLASS_NAME, 'job-view-layout.jobs-details')
        #job_element.click()
        layout = main_driver.find_element(By.CLASS_NAME, "job-view-layout.jobs-details")
        
        thread_job = ThreadWithReturnValue(target=scrap_job_info, 
                                            args=[layout])
        thread_job.start()       
        
        
        ##### Eco score Thread
        t_eco = ThreadWithReturnValue(target=get_eco_score, 
                                            args=(eco_driver, company))
        t_eco.start()        
        company_name, eco_score = '',0
        
        
        ### Thread join
        company_infos = thread_company.join()
        job_tags = thread_job.join()
        t_eco.join()        

        #job_tags += [company]
        
        
        #titles.append(job_title)
        #companies.append(company)
        #locations.append(location)
        #ids.append(job_id)
        #job_url_list.append(job_url)
        company_names.append(company_name)
        eco_scores.append(eco_score)
        
        if verbose:
            print("-------> time of append :", time.time()-deb)
            #print("!! loop_total_time : ", time.time()-deb__, end="\n\n")
    
    ###########################
    # End of loop
    ###########################
    """
    titles = []
    companies = []
    locations = []
    ids = []
    jobs_url = []
    companies_url = []
    competencies_list = []
    salaries = []
    post_type = []
    hours = []
    """
    print(reviews)
    print(addings)
    
        
    
    CEOs, founded, nb_employees, human_ratings, salary_satisfactions = addings
    df3 = pd.DataFrame({
        "CEO": CEOs,
        "Date création": founded,
        "Nb_employés": nb_employees,
        "Score humain": human_ratings,
        "Satisfaction salariale": salary_satisfactions,
        })
    # All reviews tags
    reviews_names = {tag_[0] for review in reviews for tag_ in review}    
    print(len(reviews_names))
    print(reviews_names)
    
    
    reviews_list = []
    for review in reviews:
        line = []
        for i, review_name in enumerate(reviews_names):
            temp = [tag_[0] for tag_ in review]
            if review_name in temp:
                line.append(review[temp.index(review_name)][1])
            else:
                line.append('')
        reviews_list.append(line)
        
    print(reviews_list)
    
    aaa = [titles,
companies,
locations,
ids,
job_url_list,
companies_url,
competencies_list,
salaries,
post_type,
hours,]
    
    for a in aaa:
        print(len(a))
    
    df1 = pd.DataFrame({
        "Titre": titles,
        "Entreprise": companies,
        "Lieu": locations,
        "job_id": ids,
        "url_poste": job_url_list,
        "url_company": companies_url,
        "Compétences": competencies_list,
        "Salaire": salaries,
        "Type de poste": post_type,
        "Horaires": hours,
        })
    
    df2 = pd.DataFrame(reviews_list, columns=list(reviews_names))
    df2.head()
    
    df4 = pd.DataFrame({
        "Company name eco": company_names,
        "Eco score": eco_scores,
        })
    
    df=pd.concat([df1, df3, df2, df4], axis=1)
    
    df.to_csv("indeed_jobs.csv")
        
    return df
        #try:
        #    job_element.find_element(By.XPATH, ".//span").get_attribute("title") # Title / Entreprise
        #except:
        #    bypass_captcha(driver)
        #    driver.back()
        #    stop = True
        #job_info = ""
        #
        ##Check for Captcha in loop
        #try:
        #    wait_for(driver, By.ID, "jobsearch-ViewjobPaneWrapper")
        #except:
        #    bypass_captcha(driver)
        #    driver.back()
        #    stop = True
#
        ## Look for job additionnal tags and desccription
        #try:
        #    job_info = driver2.find_element(By.ID, "jobsearch-ViewjobPaneWrapper").find_element(By.ID, 'salaryInfoAndJobType').text
        #except:
        #    job_info= "Nothing found"
        #
        #if verbose:  
        #    print("**Time of scraping on-click elements :** ", time.time()-deb)
        #    print(f"Data scrapped :\nJob Title: {job_title}\nCompany: {company}\nLocation: {location}\nJob info: {job_info}\n{'='*30}")
        
        
#def scrape_indeed_job_offers(job_title, city):
#    
#    driver = prepare_indeed_scrapping(job_title, city)
#    
#    # Extract job offers (you may need to refine this based on the actual HTML structure)
#    get_job_data(driver)
#
#    # Close the browser
#    driver.quit()