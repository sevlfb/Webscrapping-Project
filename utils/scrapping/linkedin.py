import time

import pandas as pd
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By

from utils.login import login_glassdoor
from utils.scrapping.eco_score import get_eco_score
from utils.scrapping.glassdoor import get_company_info
from utils.selenium import bypass_captcha, wait_for
from utils.threading import ThreadWithReturnValue, init_drivers


def loop_pages(list_drivers, job, location, verbose, limit, bypass):
    t = []
    dfs = []
    for drivers in list_drivers:
        t_indeed = ThreadWithReturnValue(target = get_job_data,
                                         args=(drivers, job, location, verbose, limit, bypass))
                                        #args=(drivers, verbose, bypass))
        t_indeed.start()
        t.append(t_indeed)
    for i in t:
        dfs.append(i.join())
    return dfs

def get_filters(driver):
        
    return None


def scrap_job_info(layout, company, verbose=False, bypass=False):
    print("scrap job info")
    deb = time.time()
    
    #Title
    #job_title = layout.find_element(By.CLASS_NAME,"job-details-jobs-unified-top-card__job-title-link").text
    
    job_block = layout.find_element(By.CLASS_NAME,"job-details-jobs-unified-top-card__primary-description-container")
    
    job_tags = []
    #loc_ = {"Ville": "None"}
    #### Launch this thread
    try:
        #text_to_treat = job_block.find_element(By.CSS_SELECTOR,'div:nth-child(1)').text
        #list_of_spans = [e.text for e in job_block.find_elements(By.TAG_NAME,"span")] + [company]
        #for span in list_of_spans:
        #    text_to_treat = text_to_treat.replace(span.strip(),"")
        #loc_desc = [x.strip() for x in text_to_treat.strip().split(",")]
        #loc_tags = ["Ville", "Région", "Pays"]
        #loc_ = dict(zip(loc_tags,loc_desc))
        #print("cc",company, "test",loc_,"fin", "",sep="\n")
        job_details = layout.find_elements(By.CLASS_NAME, "job-details-jobs-unified-top-card__job-insight")
        for detail in job_details:
            try:
                job_tags.append((detail.find_element(By.TAG_NAME, "li-icon").get_attribute("type"),
                                 detail.text))
            except:
                job_tags.append(('',''))      
    except:
        job_tags = []
    
    if verbose:
        print("**Time of scrapping job infos**:", time.time()-deb)
    
    #print(job_tags, loc_)
    
    return job_tags # loc_


def get_job_data(drivers, job, location, verbose=True, limit: int=None, bypass=True):
    
    
    # Get the list of all jobs and companies already searched
    #global LIST_OF_ALL_SEARCHED_JOBS
    #global LIST_OF_ALL_SEARCHED_COMPANIES
    
    #LIST_OF_ALL_SEARCHED_JOBS = 1
    #LIST_OF_ALL_SEARCHED_COMPANIES = 1
    
    print("##### INIT #####")
    # Max time for checking element. Lower = Faster
    #driver.implicitly_wait(0.1)
    
    # Assert drivers
    # driver that looks for linkedin data
    main_driver = drivers[0]
    # driver that looks for information on glassdoor
    glassdoor_drivers = drivers[1:4]
    glassdoor_drivers[0].get("https://www.glassdoor.fr/Avis/index.htm")
    # driver that looks for the ecological score of the company
    eco_driver = drivers[-1]
    # HTML Item for the job descriiption
    linkedin_jobs_url = f"https://www.linkedin.com/jobs/search/?keywords={job}&location={location}&origin=BLENDED_SEARCH_RESULT_CARD_NAVIGATION"
    main_driver.get(linkedin_jobs_url)
    
    time.sleep(1) # Safety
    
    # looking for all job offers within the page
    job_elements = main_driver.find_element(By.CLASS_NAME, "scaffold-layout__list-container").find_elements(By.XPATH, "*")
    print("NUMBER OF JOB OFFERS FOUND : ", print(len(job_elements)))
    if type(limit) == int: 
        job_elements = job_elements[:limit]
    
    if verbose:
        deb = time.time()
    
    # Captcha kills the loop of research. Captcha appears every 2.5 pages
    try:
        # if no job element -> captcha
        wait_for(job_elements[0], By.TAG_NAME, "a")
        time.sleep(1)
        job_super_ = job_elements[0].find_element(By.TAG_NAME, "a")
        job_title = job_super_.text
    except:
        if bypass:
            bypass_captcha(main_driver, method="cloudflare")
            main_driver.back()
            stop = True
    
    if verbose:
        print("**Time of Bypassing captcha :** ", time.time()-deb)
        

    # Job infos
    jobs_ids = [] # dups checking
    
    jobs_tags_list = []
    jobs_locs = []
        
    # Company infos
    companies_name = [] # dups checking
    companies_infos_list = []
    companies_reviews_list = []
    companies_add_infos = []
    
    eco_scores = []

    
    # For every job offer on the page  
    for job_element in job_elements:
        print("\n\nNEW JOB ELEMENT")
            
        #### Schema
        # Get company name
        ### Company data
        # Store company data at first look
        # At the end, check if same number columns and normalize
        ### Job data
        # Get information about job and company
        # Add company data afterwards
        
###### Get job name and ID ######
        hover = ActionChains(main_driver).move_to_element(job_element).click()
        hover.perform()
        wait_for(job_element, By.TAG_NAME, "a")
        time.sleep(1)
        job_super_ = job_element.find_element(By.TAG_NAME, "a")
        job_title = job_super_.text
        job_href = job_super_.get_attribute("href").split("/")[:6]
        print("JOB ID :", job_href)
        job_id = job_href[-1]
        wait_for(main_driver, By.CLASS_NAME, 'job-view-layout.jobs-details', 2)
        ###### Get the company name ######
        company = job_element.find_element(By.CLASS_NAME,"job-card-container__primary-description").text
        
        loc_ = job_element.find_element(By.CLASS_NAME, "job-card-container__metadata-item").text
        loc_desc = [x.strip() for x in loc_.split("(")[0].strip().split(",")]
        loc_tags = ["Ville", "Région", "Pays"]
        loc_ = dict(zip(loc_tags,loc_desc))
        print("JOB LOCATION:", loc_)
        #jobs_locs.append(loc_)
        
        # Check for dups in job (in case of process reload or dups in other linkedin page)
        if job_id in jobs_ids:
            perform_threads = False
        else:
            perform_threads = True
            jobs_ids.append((job_id, job_title, company))
        
        if perform_threads:

        ##### Job Thread #####
                        
            wait_for(main_driver, By.CLASS_NAME, 'job-view-layout.jobs-details')
            layout = main_driver.find_element(By.CLASS_NAME, "job-view-layout.jobs-details")
            
            thread_job = ThreadWithReturnValue(target=scrap_job_info, 
                                                args=[layout, company])
            thread_job.start()  
    
            # Check for dups in company name (to avoid getting early captcha and get faster process)
            if company not in companies_name:
                perform_company_threads = True
                companies_name.append(company)
            else:
                perform_company_threads = False
        
            if perform_company_threads:  
            ##### Glassdoor thread #####
                print("company:",company)
                thread_company = ThreadWithReturnValue(target=get_company_info, 
                                                    args=(glassdoor_drivers, company, verbose, bypass))
                thread_company.start()
                
            ##### Eco score Thread #####
                t_eco = ThreadWithReturnValue(target=get_eco_score, 
                                                    args=(eco_driver, company))
                t_eco.start()        
                eco_company_name, eco_score = '',0     
            
            
    ### All Threads join ####
    
            job_tags = thread_job.join() #loc_
            # List, dict
            jobs_tags_list.append(job_tags)
            jobs_locs.append(loc_)

            if perform_company_threads:
                company_agg_infos = thread_company.join() # 1 or 4 items
                print("Agg infos", company_agg_infos)
                eco_company_name, eco_score = t_eco.join()
                if company_agg_infos == "Captcha detected":
                # If the captcha is detected, we have to do the process again
                    print("##### RELOAD IMMINENT #####")
                    for driver in glassdoor_drivers:
                        driver.quit()
                    del glassdoor_drivers
                    g_email = "severin.lefebure@edu.devinci.fr"
                    g_password = "jesuisungenie"
                    glassdoor_drivers = init_drivers(3, login_glassdoor, [None, g_email, g_password, False, False])
                    drivers = drivers[0] + glassdoor_drivers[0] + drivers[-1]
                    add_data = False  
                else:
                    add_data = True
                    ### perform company threads or just quit doing maybe lose 1 data
            if add_data:
                company_infos,company_reviews_infos = company_agg_infos
                stars_infos, tags_infos, additional_infos = company_reviews_infos
                company_reviews_infos = stars_infos, tags_infos
                # List of elements, List of tuples with tag + score
                # ML for tagging elements ?
                companies_infos_list.append([tuple(company_infos)])
                companies_reviews_list.append(company_reviews_infos)
                companies_add_infos.append(additional_infos)
                
                eco_scores.append((eco_company_name, eco_score))
        
        if verbose:
            print("-------> time of append :", time.time()-deb)
            #print("!! loop_total_time : ", time.time()-deb__, end="\n\n")
    
    ###########################
    # End of loop
    ###########################
    
    def normalize_data(agg_list): #List is [(name,score),(name,score),...] and get list of unique names (columns) and associated scores (rows)
        names_ = {tag_[0] for review in agg_list for tag_ in review}    
        list_ = []
        for agg_ in agg_list:
            line = []
            for i, name_ in enumerate(names_):
                temp = [tag_[0] for tag_ in agg_]
                if name_ in temp:
                    line.append(agg_[temp.index(name_)][1])
                else:
                    line.append('')
            list_.append(line)
        return list_, names_
    
    reviews_tags_list = [item[0] for item in companies_reviews_list]
    stars_tags_list = [item[1] for item in companies_reviews_list]
    companies_reviews_tags_list, company_reviews_names = normalize_data(reviews_tags_list)
    companies_stars_tags_list, company_stars_names = normalize_data(stars_tags_list)
    jobs_tags_tags_list, job_tags_names = normalize_data(jobs_tags_list)
    companies_additional_tags_list, company_additional_names = normalize_data(companies_add_infos)

    df_glassdoor_reviews = pd.DataFrame(companies_reviews_tags_list, columns=list(company_reviews_names))
    df_glassdoor_stars = pd.DataFrame(companies_stars_tags_list, columns=list(company_stars_names))
    df_glassdoor_tags = pd.DataFrame(jobs_tags_tags_list, columns=list(job_tags_names))
    df_glassdoor_adds = pd.DataFrame(companies_additional_tags_list, columns=list(company_additional_names))
    print("companies_infos_list", len(companies_infos_list), len(companies_infos_list[0]), companies_infos_list)
    #companies_infos_list=tuple(companies_infos_list)
    df_glassdoor_list = pd.DataFrame(companies_infos_list, columns=["List of infos from company"])
    df_companies = pd.DataFrame(companies_name, columns=["Company Name"])


    #print("g_reviews", df_glassdoor_reviews.columns)
    #print("g_stars", df_glassdoor_stars.columns)
    #print("g_tags", df_glassdoor_tags.columns)
    #print("g_adds", df_glassdoor_adds.columns)
        
    df_glassdoor=pd.concat([df_companies, df_glassdoor_list, df_glassdoor_adds, df_glassdoor_tags, df_glassdoor_reviews, df_glassdoor_stars], axis=1)
    
    df_ecoscore = pd.DataFrame({
        "EcoCompany name": [score[0] for score in eco_scores],
        "Ecoscore": [score[1] for score in eco_scores],
        })

    df_company = pd.concat([df_glassdoor, df_ecoscore], axis=1)
    
    dict_companies = {}
    for i in range(df_company.shape[0]):
        line = df_company.loc[i, :].values.tolist()
        dict_companies[line[0]] = line[1:]
    
    jobs_final_list = []
    print("dictcompa_keys", dict_companies.keys())
    for i in range(len(jobs_ids)):
        jobs_final_list.append([jobs_ids[i][1], # Job Title
                                jobs_ids[i][0], # Job ID
                                jobs_tags_list[i], # Job Tags
                                jobs_ids[i][2], # Company Name
                                jobs_locs[i]] + dict_companies[jobs_ids[i][2]],
                                )

    print(len(jobs_final_list), len(jobs_final_list[0]), jobs_final_list)
    
    print()
    
    df_jobs =  pd.DataFrame(jobs_final_list, 
                            columns=["Job Title",
                                     "Job ID",
                                     "Job Tags",
                                     "Company Name",
                                     "Job Loc"
                                     ] + list(df_company.columns[1:].values)
        )
    
    
    df_jobs.to_csv("List_jobs.csv")
        
    return df_jobs
