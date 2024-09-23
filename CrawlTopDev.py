from datetime import datetime
from json import load
from selenium import webdriver
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
from dotenv import load_dotenv
import os



load_dotenv()
# credentials
password = os.getenv('GITHUB_PASSWORD')
username = os.getenv('GITHUB_USERNAME')

# init ChromeDriver with options
chrome_options = Options()
chrome_options.add_argument("--start-maximized")

driver_service = Service(executable_path='./chromedriver-win64/chromedriver.exe')
driver = webdriver.Chrome(service=driver_service, options=chrome_options)

# Navigate to TopDev login page
driver.get('https://accounts.topdev.vn/')
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="btnLoginGithub"]')))

# Click on GitHub login button
try:
    github_login_button = driver.find_element(By.XPATH, '//*[@id="btnLoginGithub"]')
    github_login_button.click()
except Exception as e:
    print("Error clicking GitHub login button:", e)
    driver.quit()

# GitHub login process
try:
    username_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="login_field"]'))
    )
    username_input.send_keys(username)

    password_input = driver.find_element(By.XPATH, '//*[@id="password"]')
    password_input.send_keys(password)

    login_button = driver.find_element(By.XPATH, '//*[@id="login"]/div[3]/form/div/input[13]')
    login_button.click()
except Exception as e:
    print("Error during GitHub login:", e)
    driver.quit()

# Wait for login to complete
WebDriverWait(driver, 10).until(EC.url_changes('https://accounts.topdev.vn/'))

# Navigate to job listing page
driver.get('https://topdev.vn/it-jobs?src=topdev.vn&medium=mainmenu')
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="frontend-v4"]')))

# Handle pop-up closing
try:
    close_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//button[@aria-label="Close"]'))
    )
    close_button.click()
except Exception as e:
    print("No pop-up found or error closing pop-up:", e)

# Scroll to load all jobs
def scroll_to_load_all_jobs():
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sleep(4)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

scroll_to_load_all_jobs()

# Store data
url_jobs = []
jobs_data = []

# Get total jobs
try:
    total = int(driver.find_element(By.XPATH, '//*[@id="frontend-v4"]/main/div[2]/div/div/div[1]/section/h1/span').text)
    print("Total jobs:", total)
except Exception as e:
    print("Error getting total jobs:", e)
    driver.quit()

# Get list of job URLs
for i in range(1, total + 1):
    try:
        urls_path = f'//*[@id="frontend-v4"]/main/div[2]/div/div/div[1]/section/ul/li[{i}]/a/div/div/div[2]/h3/a' if i <= 11 else f'//*[@id="frontend-v4"]/main/div[2]/div/div/div[1]/section/ul/div/ul/li[{i}]/a/div/div/div[2]/h3/a'
        element = driver.find_element(By.XPATH, urls_path)
        url = element.get_attribute('href')
        url_jobs.append(url)
    except Exception as e:
        print(f"Error getting URL for job {i}")
        continue

# Get data from each job
for url in url_jobs:
    driver.get(url)
    sleep(2)  # Salary element
    try:
        #-----------------Salary-----------------#
        salary = driver.find_element(By.XPATH, '//*[@id="detailJobHeader"]/div[2]/div[3]/p').text
    except Exception as e:
        salary = ""
    
    try:    
        #-----------------Location-----------------#
        location = driver.find_element(By.XPATH, '//*[@id="detailJobHeader"]/div[2]/div[1]/div/div').text
        location = location.split(',')
        location = location[-1]
    except Exception as e:
        location = ""
    
    try:    
        #-----------------Time-----------------#
        time = driver.find_element(By.XPATH, '//*[@id="detailJobHeader"]/div[2]/div[2]/div/div').text
        time = time.replace('Posted ', '')
    except Exception as e:
        time = ""
    
    try:    
        #-----------------Experience-----------------#
        min_experience = driver.find_element(By.XPATH, "//h3[text()='Minimum year of experience']/following-sibling::div/a").text
        experience = min_experience.replace('From ', '')
    except Exception as e:
        experience = ""
    
    try:    
        #-----------------Level-----------------#
        levels_div = driver.find_element(By.XPATH, '//h3[text()="Level"]/following-sibling::div')
        level_elements = levels_div.find_elements(By.TAG_NAME, 'a')
        level = ', '.join([level.text for level in level_elements])
    except Exception as e:
        level = ""
    
    try:    
        #-----------------Job Type-----------------#
        job_type = driver.find_element(By.XPATH, "//h3[text()='Job Type']/following-sibling::div/a").text
    except Exception as e:
        job_type = ""
    
    try:           
        #-----------------Contract_Type-----------------#
        contract_div = driver.find_element(By.XPATH, '//h3[text()="Contract type"]/following-sibling::div')
        contract_elements = contract_div.find_elements(By.TAG_NAME, 'a')
        contract_type = ', '.join([contract.text for contract in contract_elements])
    except Exception as e:
        contract_type = ""

    
    try:
        #-----------------Tech_Stacks-----------------#
        tech_div = driver.find_element(By.XPATH, '//h3[text()="Tech stack"]/following-sibling::div')
        tech_elements = tech_div.find_elements(By.TAG_NAME, 'span')
        tech_stacks = ', '.join([tech.text for tech in tech_elements])
    except Exception as e:
        tech_stacks = ""

    
    jobs_data.append([location, level, job_type,contract_type, experience, tech_stacks, salary, time])

today = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
# Write data to CSV
try:
    with open(f'./Data/jobs_data_{today}.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Location", "Level", "Job Type", "Contract Type", "Experience","Tech Stacks", "Salary", "Time"])
        writer.writerows(jobs_data)
    print("Successfully wrote data to CSV file.")
except Exception as e:
    print("Error writing data to CSV file:", e)

# Close the driver
driver.quit()
