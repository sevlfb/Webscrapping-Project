import streamlit as st
from st_pages import Page, _show_pages
from utils.threading import init_drivers
# from utils.processing.indeed import login_indeed_from_scratch, enter_indeed_parameters
# from utils.scrapping.indeed import get_job_data, get_filters, loop_pages
from utils.login import check_phone_popup
from utils.streamlit import filter_selectboxes
import time
import pandas as pd
##### Page config

streamlit_pages = [
    #Page("app/Main.py","Accueil", f"""{"📫" if st.session_state["saved_file"] == None else "📬"}"""),
    Page("menu.py","Accueil", "📬"),
    Page("streamlit_pages/Streamlit.py", "DataFrame", "🤖"),
    Page("streamlit_pages/df_test.py", "Dataframe test on streamlit", "")
]

_show_pages(streamlit_pages)

print("Hello")
session = st.session_state

#### Login container
login_container = st.container()
reset_drivers = st.button("Reset drivers")

if reset_drivers:
    if "drivers" in session:
        with st.spinner("Deleting the drivers..."):
            for drivers_list in session["drivers"]:
                #st.write(driver)
                for driver in drivers_list:
                    driver.quit()
            del session["drivers"]
            session["logged_in"] = False
    st.experimental_rerun()
#### Init drivers but once :
for arg in ["logged_in","select_filters","scrap"]:
    if arg not in session:
        session[arg] = False
    

#### Ensure login at very first
if not session["logged_in"] :#and "drivers" not in session:
    #if "drivers" in session:
    #    del session["drivers"]
    with login_container.container():
        email = st.text_input("Enter your email", value="scrapperselenium@gmail.com")
        password = st.text_input("Enter your password", value="Password123!*")
        submit = st.button("Submit")
        if submit:
            try:
                print("Drivers !!!!" if "drivers" in session else "No drivers ;(")
                with st.spinner("Setting up the environment"):
                    pages = 1
                    session["drivers"] = init_drivers(4,func=login_indeed_from_scratch, args=[email, password], 
                        #drivers=[] if "drivers" not in session else session["drivers"],
                         nb_pages=pages)
                    for drivers_list in session["drivers"]:
                        drivers_list.append(init_drivers()[0][0])
                        #session["drivers"][-1].set_window_position(2000,2000)
                st.write("ok")
                for i, driver in enumerate(session["drivers"]):
                    has_popup = False
                    #has_popup = check_phone_popup(driver)
                    if has_popup:
                        st.write(f"Driver {i} has phone popup", 
                                 "window handles >= 3", len(driver.window_handles))
                        st.write("Please manually connext to indeed first, then try again")
                    #send_code_phone_popup()
                st.write("lourd")
                if not has_popup:
                    session["logged_in"] = True
            except:
                #if "drivers" in session:
                #    del session["drivers"]
                st.write("Issue with login, try default parameters")
        if session["logged_in"]:
            st.experimental_rerun()
            
#### Page architecture
if session["logged_in"] and "drivers" in session:
    reset = st.button("Reset")
    job_title = st.text_input("Job", value="Data Analyst")
    location = st.text_input("Location", value="Paris")
    get_data = st.button("Submit")
    if reset:
        session["logged_in"] = False
        print(session["drivers"])
        #del session["drivers"]
        st.experimental_rerun()
    if get_data or session["select_filters"]:
        #session["drivers"][0] = \
        #    enter_indeed_parameters(session["drivers"][0], job_title, location)
        if get_data:
            session["select_filters"] = False
        if not session["select_filters"]:
            session["drivers"][0][0].get(f"https://fr.indeed.com/jobs?q={job_title}&l={location}")
            session["filters"] = get_filters(session["drivers"][0][0])
            #st.write(session["filters"])
            session["select_filters"] = True
        filter_selectboxes(session["filters"], columns=3)
        submit_button = st.button("Submit2")
        if submit_button:
            salary=""
            session["select_filters"]=False
            link = "?q={job_title}{salary}&l={location}"
            for i, (filter, values) in enumerate(session["filters"].items()):
                #st.write(i, filter, values, st.session_state[f"filter_{i}"])
                data = session["filters"][filter][st.session_state[f"filter_{i}"]]
                if filter == "Salaire":
                    salaire_ = "+" + data
                else:
                    link += "" if len(data) == 0 else f"&{data}"
            link = link.replace("sc::","sc=0kf%3A", 1)
            link = link.replace("&sc::","")
            temp = link.count("%%%%")
            if temp > 0 : link = link.replace("%%%%","", temp-1)
            link = link.replace("%%%%","%3B")
            link = link.format(job_title=job_title.lower().replace(" ", "+"),
                               salary=salaire_,
                               location=location)
            st.write(link)
            for drivers_list in session["drivers"]:
                drivers_list[0].get("https://fr.indeed.com/emplois"+link)
            with st.spinner("OKKKKKK LET'S GOOOOO"):
                deb = time.time()
                dfs = loop_pages(session["drivers"], verbose=False, bypass=True)
                try:
                    df=pd.concat(dfs)
                except:
                    st.write("Error")
                st.write(f"exec in {time.time()-deb} seconds")
            #st.dataframe(df)
 
       # get_job_data(session["drivers"])


#### conditions