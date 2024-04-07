#imports 
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
from selenium.webdriver.common.keys import Keys
import pandas

options = Options()
options.add_experimental_option("detach", True) 
options.add_experimental_option("excludeSwitches", ["enable-automation"]) 

driver = webdriver.Chrome(options=options, service=Service(ChromeDriverManager().install()))

driver.get("https://www.linkedin.com/jobs/search?trk=guest_homepage-basic_guest_nav_menu_jobs&position=1&pageNum=0")
while True:    
    time.sleep(5)
    try:
        search = driver.find_element(By.ID, "job-search-bar-keywords")
        location = driver.find_element(By.ID, "job-search-bar-location")
    
    except: #because refreshing isn't enough to bypass the login page
        print('cannot find elements')
        driver.quit()
        driver = webdriver.Chrome(options=options, service=Service(ChromeDriverManager().install()))
        driver.get("https://www.linkedin.com/jobs/search?trk=guest_homepage-basic_guest_nav_menu_jobs&position=1&pageNum=0")

    else: 
        search.clear()
        location.clear()
        time.sleep(2)
        location.send_keys(input("enter Location: "))
        time.sleep(2)
        search.send_keys(input("enter field: "))
        time.sleep(2)
        search.send_keys(Keys.ENTER)
        time.sleep(10)

        collected_jobs = []

        #get the total number of jobs in case needed
        results = driver.find_element(By.CSS_SELECTOR, "span.results-context-header__job-count").text
        if results.endswith('+'):
            results = results[:-1]
        results = results.replace(',', '')
        results = int(results) 

        while len(collected_jobs) < 100:
                time.sleep(2)
                try:
                    morebtn = driver.find_element(By.CSS_SELECTOR, "button.infinite-scroller__show-more-button")
                    morebtn.click()
                except:
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                try:
                    listOfJobs = driver.find_elements(By.CSS_SELECTOR, "ul.jobs-search__results-list li")
                except:
                    print("NO jobs found")
                    break 
                else:          
                    listLen = len(collected_jobs)        
                    time.sleep(5)  # Add a short delay to allow new jobs to load
                    new_jobs = [job for job in listOfJobs if job not in collected_jobs]
                    collected_jobs.extend(new_jobs)
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);") #scrolls to the bottom of the page
                    
                    if(listLen == len(collected_jobs)):  
                        driver.execute_script("window.scrollBy(0, -250);") #scrolls up a bit because there can be a problem with loading new jobs on linkedIn's end
                    
        print(f"Job collection complete, with {len(collected_jobs)} jobs")

        all_jobs = []
        for job in collected_jobs:
            title = job.find_element(By.CSS_SELECTOR, "h3.base-search-card__title").text
            company = job.find_element(By.CSS_SELECTOR, "h4.base-search-card__subtitle").text
            location = job.find_element(By.CSS_SELECTOR, "span.job-search-card__location").text

            try: 
                clink = job.find_element(By.CLASS_NAME, "hidden-nested-link").get_attribute("href")
            except:    
                clink = "no link"
            try:
                link = job.find_element(By.CLASS_NAME, "base-card__full-link").get_attribute("href")
            except:    
                link = "no link"
            try:
                timee = job.find_element(By.CLASS_NAME, "job-search-card__listdate").text   
            except:
                timee = "undefined"     

            job_info = {"time": timee, "title": title, "company": company, "location": location, "job-link": link, "company-link": clink}

            all_jobs.append(job_info) 

        df = pandas.DataFrame(all_jobs)
        file_name = input("enter file name: ") + ".csv"
        df.to_csv(file_name)