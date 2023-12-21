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


def scrap_in_page_elements(job_element):
# Scrap elements of the job offers         #In page information
    job_title = job_element.find_element(By.TAG_NAME, "span").get_attribute("title") #.text # Title
    company = job_element.find_element(By.CSS_SELECTOR, '[data-testid="company-name"]').text # company
    location = job_element.find_element(By.CSS_SELECTOR, '[data-testid="text-location"]').text # location
    job_id = job_element.find_element(By.TAG_NAME, "span").get_attribute("id").split("-")[1] # ID
    job_link = job_element.find_element(By.TAG_NAME, 'a').get_attribute("href")
    job_url = "https://fr.indeed.com/viewjob?jk={job_id}".format(job_id=job_id)
    return [job_title, company, location, job_id, job_url, job_link]


def scrap_company_info(driver, company_link, verbose=False, bypass=False):
    
    deb = time.time()
    
    company_infos_list = []
    #print("company link :", company_link)
    driver.get(company_link)
    
    locator = (By.CSS_SELECTOR, '[itemprop="name"]')
    
    if not wait_for(driver, *locator, 1) and bypass: 
        bypass_captcha(driver, method="cloudflare")

    if verbose:
        print("**REVIEWS !!!!!! Time of getting + bypass**:", time.time()-deb)
        
    #
    locators = [(By.CSS_SELECTOR, '[data-testid="CeoWidget-title"]'),
    (By.CSS_SELECTOR, '[data-testid="companyInfo-founded"]'),
    (By.CSS_SELECTOR, '[data-testid="companyInfo-employee"]'),
    (By.CSS_SELECTOR, '[data-testid="CeoWidget-humanRating-rating"]'),
    (By.CLASS_NAME, 'cmp-SalarySatisfactionSidebarWidgetPieChart-inside')]#'class="cmp-SalarySatisfactionSidebarWidgetPieChart-inside"']
    
    
    for i, locator in enumerate(locators):
        try:
            a = driver.find_element(*locator).text.split("\n")[-1]
            print(a)
            company_infos_list.append(a)
        except:
            company_infos_list.append('')
    
    if verbose:
        print("-"*4*2+"> Time of scrapping company infos**:", time.time()-deb)
        deb = time.time()
    
    return company_infos_list

def scrap_review_info(driver2, reviews_url, verbose=False, bypass=False):
    deb = time.time()
    driver2.get(reviews_url)
    try:
        try:
            nb_avis = driver2.find_element(By.CSS_SELECTOR, '[data-tn-element="reviews-tab"]').text[0]
        except:
            nb_avis = 0
        #print("1")
        a = list(map(lambda x: x.text, driver2.find_element(By.CSS_SELECTOR, '[data-testid="topic-filter-list"]').find_elements(By.TAG_NAME, 'span')))
        reviews_notes = [a[i] for i in range(0, len(a), 3)]
        reviews_tags = [a[i] for i in range(2, len(a), 3)]
        list__ = [(j,i) for i,j in zip(reviews_notes,reviews_tags)]
        print("-"*4*2+"> Time of reviews : ",time.time()-deb)
        return list__
    except:
        return [('','')]




def scrap_job_info(drivers, job_link, verbose=False, bypass=False):
    
    deb = time.time()
    #print(len(drivers))
    lookup_driver, company_driver, review_driver = drivers
    #print(review_driver.getCurrentURL())
    lookup_driver.get(job_link)
    #if verbose:
    #    print("**JOBS !!!!!! Time of getting**:", time.time()-deb)
    
    # get obvious element then bypass  
    if bypass: bypass_captcha(lookup_driver, method="cloudflare")
    if verbose:
        print("**JOBS !!!!!! Time of getting + bypass**:", time.time()-deb)
    
    
    locator = (By.CSS_SELECTOR, '[data-testid="list-item"]')
    locator_company = (By.CSS_SELECTOR, '[data-testid="inlineHeader-companyName]')
    wait_for(lookup_driver, *locator_company, 30)
    
    try:
        company_link = lookup_driver.find_element(By.CSS_SELECTOR, '[data-testid="jobsearch-CompanyInfoContainer"]')\
            .find_element(By.TAG_NAME, 'a').get_attribute("href").split("?")[0]
    except:
        company_link = ''
    
    reviews_url=f"{company_link}/reviews"

    ### Threads ###
    if company_link != '':
        t_company = ThreadWithReturnValue(target=scrap_company_info, 
                                            args=(company_driver, company_link, verbose, bypass))
        t_company.start()
        
        t_reviews = ThreadWithReturnValue(target=scrap_review_info, 
                                            args=(review_driver, reviews_url, verbose, bypass))
        t_reviews.start()
    
        #print("supposed to wait")
        
        result_info = np.array(t_company.join()).reshape(-1,1)
        #print("RESULT INFO !!!!!!!!!!!!", len(result_info))
        #print("result_info", result_info)
        
        reviews_append = t_reviews.join()
        #print("reviews_append", reviews_append)
    else:
        result_info = np.array(['']*5).reshape(-1,1)
        reviews_append = [('','')]

    #salaries_url=f"{company_link}/salaries"
    #jobs_url=f"{company_link}/jobs"

    # Get the set of all different tags afterwards 
    # Do a list of values for all tags with empty values
    # Be a fucking genius
    
    #'data-testid="topic-filter-list"'
    #'data-tn-element="review-filter-wlbalance"' #span text
    #'data-tn-element="review-filter-paybenefits"'
    #'data-tn-element="review-filter-jobsecadv"'
    #'data-tn-element="review-filter-mgmt"'
    #'data-tn-element="review-filter-culture"'
    
    # Get all the different tags and ratings
    # Create Thread 3
    
    list_items = lookup_driver.find_elements(*locator)
    competencies = list(item.text for item in list_items)
    #print("Competencies:", competencies, end = " | ")
    tags = ['Salaire', 'Type de poste', 'Horaires et roulements']
    # Get all tags
    try:
        #print("Job info:")
        locator = (By.ID, 'jobDetailsSection')
        list_items = lookup_driver.find_element(*locator)
        elements = list_items.text.split("\n")
        infos = []
        for tag in tags:
            if tag in elements:
                infos.append((tag, elements.index(tag)))
        infos.append(('end', len(elements)))
        if len(infos)>0:
            infos.sort(key=(lambda x: x[1]))
        info_dic = {}
        for tag in tags:
            info_dic[tag] = []
        for i, info in enumerate(infos[:-1]):
            info_dic[info[0]] = elements[info[1]+1:infos[i+1][1]]
        #print(info_dic if info_dic else print("No additionnal categories"))
    except:
        info_dic = {}
        for tag in tags:
            info_dic[tag] = ''
        print("No job detail section !") 
    
    if verbose:
        print("-"*4*1+"> Time of scrapping job infos**: ", time.time()-deb)
        deb = time.time()
        
    
    # Glassdoor
    'placeholder="Lieu"'
    'placeholder="Votre intitulé de poste"'
    
    
    'data-test="salary-details-total-pay-tooltip-badge"'
    'data-test="confidence-badge"'
    
    if verbose:
        print("**Time of scrapping reviews infos**:", time.time()-deb)
    
    
    return info_dic, competencies, result_info, reviews_append, company_link # Dict, column, list


def get_job_data(drivers, verbose=True, limit=None, bypass=True):
    # Max time for checking element. Lower = Faster
    #driver.implicitly_wait(0.1)
    
    main_driver = drivers[0]
    #if len(drivers) >= 1: lookup_driver = drivers[1]
    #if len(drivers) >= 2: company_driver = drivers[2]
    #if len(drivers) >= 3: reviews_driver = drivers[3]
    
    # HTML Item for the job description
    indeed_css_job_box = '[data-testid="slider_item"]'
    job_elements = main_driver.find_elements(By.CSS_SELECTOR, indeed_css_job_box)
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
    
    loca = (By.ID, "google-Only-Modal-Button")
    
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
        
        if verbose:
            deb__ = time.time()
        
        if verbose:
            deb = time.time()
            
        # Scrap elements of the job offers         #In page information
        job_title, company, location, job_id, job_url, job_link = scrap_in_page_elements(job_element)
        
        titles.append(job_title)
        companies.append(company)
        locations.append(location)
        ids.append(job_id)
        job_url_list.append(job_url)

        #print(job_link)
        if verbose:
            print("**Time of scraping in-page elements : **", time.time()-deb)
        
        # Job information
        #print(f"job link : {job_link}")
        
        # Thread for eco_score
        t_eco = ThreadWithReturnValue(target=get_eco_score, 
                                            args=(drivers[-1], company))
        t_eco.start()        
        company_name, eco_score = '',0
        
        # Create Thread 1
        t1 = ThreadWithReturnValue(target=scrap_job_info, args = [drivers[1:4], job_link, verbose, bypass])
        t1.start()
        #time.sleep(15)
        values = t1.join()
        company_name, eco_score = t_eco.join()
        #print("\nvalues\n")
        #for i in values:
        #    print(i)
        info_dic, competencies, result_info, reviews_append, company_url = values # Dict, column, list
        #print("\nvalues\n")
        
        deb = time.time()
        
        competencies_list.append(competencies)
        salaries.append(info_dic["Salaire"])
        post_type.append(info_dic["Type de poste"])
        hours.append(info_dic["Horaires et roulements"])
        companies_url.append(company_url)
        addings = np.append(addings, result_info, axis = 1)
        company_names.append(company_name)
        eco_scores.append(eco_score)
        reviews.append(reviews_append)
        
        if verbose:
            print("-------> time of append :", time.time()-deb)
            print("!! loop_total_time : ", time.time()-deb__, end="\n\n")
    
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