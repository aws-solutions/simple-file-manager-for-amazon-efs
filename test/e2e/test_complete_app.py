import pytest
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options


@pytest.fixture
def browser():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    browser = webdriver.Chrome(chrome_options=chrome_options)
    return browser

def test_complete_app(browser, testing_env_variables):
    browser.implicitly_wait(5)
    browser.get(testing_env_variables['SFM_ENDPOINT'])

    # Login

    username_field = browser.find_element_by_xpath("/html/body/div/div[2]/div/div/div/div/div/div[2]/div[1]/div/input")
    username_field.send_keys(testing_env_variables['SFM_USERNAME'])
    password_field = browser.find_element_by_xpath("/html/body/div/div[2]/div/div/div/div/div/div[2]/div[2]/input")
    password_field.send_keys(testing_env_variables['SFM_PASSWORD'])
    browser.find_element_by_xpath("/html/body/div/div[2]/div/div/div/div/div/div[3]/span/button").click()
    
    time.sleep(5)
    
    # Open file manager lambda creation page

    filesystem_element = browser.find_element_by_xpath("/html/body/div/div[2]/div/div/div/div/div/div/table/tbody/tr[1]/td[3]/div/p")

    assert filesystem_element.text == testing_env_variables['FILESYSTEM_ID']
   
    browser.find_element_by_xpath("/html/body/div/div[2]/div/div/div/div/div/div/table/tbody/tr[1]/td[2]/div/a").click()
   
    # Click file manager lambda submit button
   
    browser.find_element_by_xpath("/html/body/div/div[2]/div/div/div/div[1]/form/button").click()

    time.sleep(30)

    creating_element = browser.find_element_by_xpath("/html/body/div/div[2]/div/div/div/div/div/div/table/tbody/tr[1]/td[2]/div/a")
    assert creating_element.text == "Creating"

    # Wait for lambda to be created

    time.sleep(270)

    browser.refresh()

    # Open filesystem page

    browser.find_element_by_xpath("/html/body/div/div[2]/div/div/div/div/div/div/table/tbody/tr[1]/td[3]/div/a").click()
    
    # Create directory
    
    browser.find_element_by_xpath("/html/body/div/div[2]/div/div/div[1]/div/div/div/div[3]/button").click()
    mkdir_input = browser.find_element_by_xpath("/html/body/div[2]/div[1]/div/div/div/div/div/div/div/form/input")
    current_time = str(time.time()).split('.')[0]
    
    mkdir_input.send_keys(current_time)

    browser.find_element_by_xpath("/html/body/div[2]/div[1]/div/div/div/div/div/div/div/form/button").click()
    
    time.sleep(5)

    dir_object = browser.find_element_by_xpath("/html/body/div/div[2]/div/div/div[1]/div/div/table/tbody/tr[1]/td/button")
    
    assert dir_object.text == current_time

    # Upload file

    browser.find_element_by_xpath("/html/body/div/div[2]/div/div/div[2]/div/div/div[1]/div[2]/button").click()
    
    browser.find_element_by_xpath("/html/body/div[2]/div[1]/div/div/div/div/div/div/div/div[1]/div/input").send_keys(testing_env_variables['MEDIA_PATH'] + testing_env_variables['FILE'])
    
    time.sleep(5)

    browser.find_element_by_xpath("/html/body/div[2]/div[1]/div/div/div/div/div/div/div/div[2]/button").click()

    file_name = browser.find_element_by_xpath("/html/body/div/div[2]/div[2]/div/div[2]/div/div/div[2]/table/tbody/tr/td/div/div[1]")
    
    time.sleep(5)

    assert file_name.text == testing_env_variables['FILE']

    # Download file
    browser.find_element_by_xpath("/html/body/div/div[2]/div/div/div[2]/div/div/div[2]/table/tbody/tr/td/div/div[3]/a").click()

    time.sleep(5)

    download_status = browser.find_element_by_xpath("/html/body/div/div[2]/div[1]")

    assert "Download completed successfully!" in download_status.text

    time.sleep(5)

    # Delete file
    browser.find_element_by_xpath("/html/body/div/div[2]/div/div/div[2]/div/div/div[2]/table/tbody/tr/td/div/div[2]/a").click()
    time.sleep(5)

    delete_status = browser.find_element_by_xpath("/html/body/div/div[2]/div[1]")
    
    assert "File deleted successfully!" in delete_status.text

    # Sign out
    browser.find_element_by_xpath("/html/body/div/div[1]/nav/ul[2]/div/div/button").click()