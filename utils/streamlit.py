from utils.threading import init_drivers_instances
from utils.processing.linkedin import setup_linkedin
from utils.login import login_glassdoor
from utils.selenium import create_driver



import streamlit as st
def filter_selectboxes(filters: dict, columns=4):
    nb_columns = columns
    nb_rows = len(filters)//nb_columns+1
    for i in range(nb_rows):
        exec(f"cols{i} = st.columns(nb_columns)")

    #st.write(filter, filters[filter])
    for i, filter in enumerate(filters):
        row = str(i//nb_columns)
        column = str(i%nb_columns)
        col_ = f"cols{row}[{column}]"
        exec(f"""st.session_state["filter_{i}"] = {col_}.selectbox(label="{filter}", options=list((map(lambda x: x.strip(), filters["{filter}"]))), index=0)""")

    link = ""
    for i, (filter, values) in enumerate(filters.items()):
        #st.write(i, filter, values, st.session_state[f"filter_{i}"])
        data = filters[filter][st.session_state[f"filter_{i}"]]
        link += "" if len(data) == 0 else f"&{data}"
        
        
        
def setup_drivers():
    nb_pages = 1

    l_email = "scrapperselenium@gmail.com"
    l_password= "Password123!*"

    g_email = "severin.lefebure@edu.devinci.fr"
    g_password = "jesuisungenie"
    job = "Data Analyst"
    city = "Paris"

    linkedin_func = setup_linkedin
    linkedin_nb_drivers = 1
    l_args = [None, l_email, l_password, False, False]

    glassdoor_func = login_glassdoor
    glassdoor_nb_drivers = 3
    g_args = [None, g_email, g_password, False, False]

    eco_func = create_driver
    eco_nb_drivers = 1
    eco_args = [False]

    processes = init_drivers_instances(nb_pages, (linkedin_func,linkedin_nb_drivers,l_args),
                        (glassdoor_func,glassdoor_nb_drivers,g_args),
                        (eco_func, eco_nb_drivers, eco_args))
    
    return processes
