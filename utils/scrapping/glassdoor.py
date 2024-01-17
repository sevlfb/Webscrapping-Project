import time

from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from utils.selenium import bypass_captcha, wait_for
from utils.threading import ThreadWithReturnValue

# Glassdoor
'placeholder="Lieu"'
'placeholder="Votre intitulé de poste"'
'data-test="salary-details-total-pay-tooltip-badge"'
'data-test="confidence-badge"'


def scrap_company_info(driver: Chrome, link, verbose, bypass):
    print("scrap company info")
    driver.get(link)
    if not bypass_captcha(driver,method="cloudflare"):
        wait_for(driver, By.CLASS_NAME, "employer-overview__employer-overview-module__employerDetails", 1)
        try:
            company_infos_block = driver.find_element(By.CLASS_NAME, "employer-overview__employer-overview-module__employerDetails")
            company_infos = list(map(lambda x: x.text, company_infos_block.find_elements(By.TAG_NAME, 'li')))
            return company_infos
        except:
            print("No employer detail")
            return []
    else:
        return "Captcha detected"
        

def scrap_reviews_info(driver: Chrome, review_url):
    print("scrap reviews_info")
    deb = time.time()
    driver.get(review_url)
    if not bypass_captcha(driver,method="cloudflare"):
        # get notes for each tag
        
        if len(driver.find_elements(By.CLASS_NAME, 
'review-overview__review-overview-module__industryAverageContainer')) > 0:
            method = "container"
        else:
            method= "click"
        
        method="click"

        
        if method == "click":
            
            driver.find_element(By.CLASS_NAME, "v2__EIReviewsRatingsStylesV2__ratingInfo").click()

            reviews_notes = driver.find_elements(By.CLASS_NAME, "accordion__AccordionStyle__header.categoryRating")
            tags_scores = [(review.text.split("\n")[0], review.text.split("\n")[-1]) for review in reviews_notes]
              
            #data-accordion-category="recommend"
            #data-accordion-category="ceoRating"
            #data-accordion-category="bizOutlook"
            
            #class="donut__DonutStyle__donutchart d-block"
            
            
            rows = driver.find_elements(By.CLASS_NAME, "barRow")
            stars_scores = [(row.text.strip(), 
              row.find_element(By.CLASS_NAME, "barFill").get_attribute("style").split(":")[1].strip())
             for row in rows
             ]
            
        if method == "container":
            try:
                block = driver.find_element(By.CLASS_NAME, 
                                            'review-overview__review-overview-module__industryAverageContainer')
                a = list(map(lambda x: x.text, block.find_elements(By.TAG_NAME, 'p')))
                reviews_notes = [a[i] for i in range(0, len(a), 2)]
                reviews_tags = [a[i] for i in range(1, len(a), 2)]
                tags_scores = [(j,i) for i,j in zip(reviews_notes,reviews_tags)]
            except:
                tags_scores = [('','')]
            # add the domain comparison !!!!!!!!!!!!
            #class="tooltip__tooltip-module__TooltipTrigger TooltipTriggerContent" hover + class="tooltip__tooltip-module__TooltipContent".text
            
            # get stars ranking %
            try:
                block = driver.find_element(By.CLASS_NAME, 
                            'review-overview__review-overview-module__distributionContainer')
                a = list(map(lambda x: x.text, block.find_elements(By.TAG_NAME, 'p')))
                reviews_notes = [a[i] for i in range(0, len(a), 2)]
                reviews_tags = [a[i] for i in range(1, len(a), 2)]
                stars_scores = [(i,j) for i,j in zip(reviews_notes,reviews_tags)]
            except:
                stars_scores = [('','')]
        
        print("scores")
        print(tags_scores, stars_scores)
        body = driver.find_element(By.CLASS_NAME, "gdGrid")
        try:
            note_globale = driver.find_element(By.CLASS_NAME, "v2__EIReviewsRatingsStylesV2__ratingInfo").text.split("\n")[0]
            print(1.1)
            recommandation_to_friend = body.find_element(By.ID, 'EmpStats_Recommend').get_attribute("data-percentage")+"%"
            print(1.2)
            CEO_approval = body.find_element(By.ID, "EmpStats_Approve").get_attribute("data-percentage")+"%"
            print(1.3)
            CEO = body.find_elements(By.CLASS_NAME, "donut-text.pt-sm.pt-lg-0.pl-lg-sm")[-1].find_element(By.TAG_NAME, "div").text
            print(1.4)
        except:
            try:
                note_globale = driver.find_element(By.CLASS_NAME, "v2__EIReviewsRatingsStylesV2__ratingInfo").text.split("\n")[0]  #v2__EIReviewsRatingsStylesV2__ratingNum.v2__EIReviewsRatingsStylesV2__large
                print(2.1)
                recommandation_to_friend = driver.find_elements(By.CLASS_NAME, 'donut__DonutStyleV2__donuttext.donut-text.pt-lg-0.px-lg-sm')[0].text.split("%")[0]
                print(2.2)
                #CEO = driver.find_element(By.CLASS_NAME, "review-overview__review-overview-module__ceoName").text
                
                CEO = body.find_elements(By.CLASS_NAME, "donut-text.pt-sm.pt-lg-0.pl-lg-sm")[-1].find_element(By.TAG_NAME, "div").text
                CEO_approval = driver.find_elements(By.CLASS_NAME, "donut__DonutStyleV2__donuttext.donut-text.pt-lg-0.px-lg-sm")[1].text.split("%")[0]
                print(2.3)
                print(note_globale,recommandation_to_friend,CEO_approval,CEO)
            except:
                note_globale='None'
                recommandation_to_friend='None'
                CEO='None'
                CEO_approval='None'
        
        company_infos = [('Note globale',note_globale), 
        ("Recommandation de l'entreprise", recommandation_to_friend),
        ('CEO', CEO),
        ('CEO Approval', CEO_approval)]
        
        print("tag/star/comp", tags_scores, stars_scores, company_infos)
        
        return tags_scores, stars_scores, company_infos
    else:
        return "Captcha detected"


def get_company_info(drivers, company, verbose=False, bypass=False):
    print("get company info")
    search_driver, company_driver, review_driver = drivers
    
    bypass_captcha(search_driver, method="cloudflare")
    wait_for(search_driver, By.ID, "companyAutocomplete-companyDiscover-employerSearch", 5)
    
    input_c = search_driver.find_element(By.ID, "companyAutocomplete-companyDiscover-employerSearch")
    input_c.send_keys(Keys.CONTROL,"a")
    input_c.send_keys(Keys.DELETE)
    input_c.send_keys(company)
    input_c.send_keys(Keys.ENTER)
    sugg = search_driver.find_element(By.CLASS_NAME,"suggestions.down")
    tries = 0
    while len(comps := sugg.find_elements(By.XPATH,"*")) == 0 and tries < 5:
        time.sleep(0.1)
        tries+=1
        print(tries)
    
    is_company=True
    
    company_infos = []
    company_reviews_infos = [
            [('','')],
            [('','')],
            [('Note globale',"None"), 
        ("Recommandation de l'entreprise", "None"),
        ('CEO', "none"),
        ('CEO Approval', "None")]
        ]
    
    
    if tries == 5:
        is_company = False
    
    if is_company:
        try:
            company_id = "E"+comps[0].find_element(By.TAG_NAME, "img").get_attribute("src").split("/")[4] 
            search_company = True
        except:
            search_company=False
            
        if search_company:
            # Thread
            print("glassdoor company", company)
            company_url = f"https://www.glassdoor.fr/Présentation/Travailler-chez-{company}-EI_I{company_id}.htm"
            company_reviews_url = f"https://www.glassdoor.fr/Avis/{company.replace(' ', '-')}-Avis-{company_id}.htm"
            
            ### Thread 1
            thread_company = ThreadWithReturnValue(target=scrap_company_info, 
                                                args=(company_driver, company_url, verbose, bypass))
            thread_company.start()

            ### Thread 2  
            thread_reviews = ThreadWithReturnValue(target=scrap_reviews_info, 
                                                args=(review_driver, company_reviews_url))
            thread_reviews.start()
            

            company_infos = thread_company.join() # 1 item
            company_reviews_infos = thread_reviews.join() # 3 items
            
            if "Captcha detected" in [company_infos, company_reviews_infos]:
                return "Captcha detected"
            
        
    if verbose:
        #print("-"*4*2+"> Time of scrapping company infos**:", time.time()-deb)
        deb = time.time()
    
    print("comp/reviews", company_infos, company_reviews_infos)
    
    return company_infos, company_reviews_infos
