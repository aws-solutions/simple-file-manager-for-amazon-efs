## Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
## SPDX-License-Identifier: Apache-2.0
import pytest
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains



@pytest.fixture
def browser():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    browser = webdriver.Chrome(options=chrome_options)
    return browser

def test_complete_app(browser, testing_env_variables):
    browser.implicitly_wait(5)
    browser.get(testing_env_variables['SFM_ENDPOINT'])

    # Login

    username_field = browser.find_element(By.XPATH, "/html/body/div/div/div/div/div/div/div/div/div[2]/div[1]/div/input")
    
    username_field.send_keys(testing_env_variables['SFM_USERNAME'])
    
    password_field = browser.find_element(By.XPATH, "/html/body/div/div/div/div/div/div/div/div/div[2]/div/input")
    
    password_field.send_keys(testing_env_variables['SFM_PASSWORD'])

    browser.find_element(By.XPATH, "/html/body/div/div/div/div/div/div/div/div/div[3]/span/button").click()

    time.sleep(5)
    
    # Click the first non-managed filesystem to create a file manager lambda

    browser.find_element(By.XPATH, "/html/body/div/div/div/div/div/div/div/div/div/div/table/tbody/tr/td[2]/div/a[text()='false'][1]").click()
   
    # Click file manager lambda submit button
   
    browser.find_element(By.XPATH, "/html/body/div/div/div/div/div/div/div/form/div[4]/button").click()

    time.sleep(15)

    creating_element = browser.find_element(By.XPATH, "/html/body/div/div/div/div/div/div/div/div/div/div/table/tbody/tr/td[2]/div/a")
    assert creating_element.text == "Creating"

    # Wait for lambda to be created

    time.sleep(300)

    browser.refresh()

    # Open filesystem page

    browser.find_element(By.XPATH, "/html/body/div/div/div/div/div/div/div/div/div/div/table/tbody/tr/td[3]/div/a").click()
    
    # Create directory
    
    browser.find_element(By.XPATH, "/html/body/div/div/div/div/div/div/div/div/div[3]/button[1]").click()
    mkdir_input = browser.find_element(By.XPATH, "/html/body/div/div/div/div/div/div/div/div/div/div/div/div/div/div/div/div/div/form/div/input")
    current_time = str(time.time()).split('.')[0]
    
    mkdir_input.send_keys(current_time)

    browser.find_element(By.XPATH, "/html/body/div/div/div/div/div/div/div/div/div[3]/div/div/div/div[2]/div/div/div/div/form/div[2]/button").click()

    time.sleep(5)

    dir_object = browser.find_element(By.XPATH, "/html/body/div/div/div/div[2]/div/div/div/table/tbody/tr/td/button")
    
    assert dir_object.text == current_time

    # Upload file

    browser.find_element(By.XPATH, "/html/body/div/div/div/div[2]/div/div[2]/div/div/div[2]/button").click()

    browser.find_element(By.XPATH, "/html/body/div/div/div/div[2]/div/div[2]/div/div/div[2]/div/div/div/div[2]/div/div/div/div/div/div/div/input").send_keys(testing_env_variables['MEDIA_PATH'] + testing_env_variables['FILE'])
    browser.find_element(By.XPATH, "/html/body/div/div/div/div/div/div[2]/div/div/div[2]/div/div/div/div[2]/div/div/div/div/div[2]/button").click()

    time.sleep(5)
    
    # Sometimes the directory overlay is still present and will block the next action. Sending an ESC closes the overlay.
    ActionChains(browser).send_keys(Keys.ESCAPE).perform()

    file_name = browser.find_element(By.XPATH, "/html/body/div/div/div/div[2]/div/div[2]/div/div[2]/table/tbody/tr/td/div/div[1]")
    
    time.sleep(5)

    assert file_name.text == testing_env_variables['FILE']

    # Download file
    browser.find_element(By.XPATH, "/html/body/div/div/div/div[2]/div/div[2]/div/div[2]/table/tbody/tr/td/div/div[3]/a").click()

    time.sleep(5)

    # Sometimes the download overlay is still present and will block the next action. Sending an ESC closes the overlay.
    ActionChains(browser).send_keys(Keys.ESCAPE).perform()

    download_status = browser.find_element(By.XPATH, "/html/body/div/div/div/div[1]")

    assert "Download completed successfully!" in download_status.text

    time.sleep(5)

    # Delete file
    browser.find_element(By.XPATH, "/html/body/div/div/div/div[2]/div/div[2]/div/div[2]/table/tbody/tr/td/div/div[2]/a").click()

    time.sleep(5)

    delete_status = browser.find_element(By.XPATH, "/html/body/div/div/div/div")
    
    assert "File deleted successfully!" in delete_status.text
    
    # Navigate home

    browser.find_element(By.XPATH, "/html/body/div/div/nav/div/a").click()

    time.sleep(5)

    # Delete resources

    browser.find_element(By.XPATH, "/html/body/div/div/div/div/div/div/div/div/div/div/table/tbody/tr/td[2]/div/a").click()
    
    time.sleep(5)
    
    browser.find_element(By.XPATH, "/html/body/div/div/div/div/div/button").click()

    time.sleep(5)
    
    deleting_status = browser.find_element(By.XPATH, "/html/body/div/div/div/div/div/div/div/div/div/div/table/tbody/tr/td[2]/div/a")
    
    assert "Deleting" in deleting_status.text

    time.sleep(120)

    browser.refresh()
    
    false_status = browser.find_element(By.XPATH, "/html/body/div/div/div/div/div/div/div/div/div/div/table/tbody/tr[1]/td[2]/div/a")

    assert "false" in false_status.text

    # Sign out
    browser.find_element(By.XPATH, "/html/body/div/div/nav/div/div/div/div/button").click()