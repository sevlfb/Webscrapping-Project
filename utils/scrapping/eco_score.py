import time

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


def get_eco_score(driver, company):
    deb = time.time()
    # Ouverture du driver
    driver.get("https://wearegreen.io/entreprises")

    # Récupère le champ de recherche 
    search_box = driver.find_element(By.ID, "searchBar")

    # Effectue une recherche avec l'entreprise souhaitée
    search_box.send_keys(company)
    search_box.send_keys(Keys.RETURN)

    time.sleep(1)
    # On récupère le premier élément de la recherche
    listres = driver.find_elements(By.CLASS_NAME,"companyCard")
    try:
        res = listres[0]
        # Affichage du nom de l'entreprise récupérée
        name = res.find_element(By.CLASS_NAME,"name")
        #print(nom.text)

        # On récupère l'image et on la traite pour récuperer le score
        images = res.find_elements(By.TAG_NAME,"img")[1:]

        score = 0
        for i,image in enumerate(images):
            if "no" in image.get_attribute('src').lower():
                score = i 
                break
        
        #print(name.text, score)
        print("-"*4*1+"> Time of eco_score", time.time()-deb)
        return name.text, score
    except:
        print("-"*4*1+"> Time of eco_score", time.time()-deb)
        return company,0
