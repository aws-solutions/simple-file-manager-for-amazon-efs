import pytest
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.alert import Alert

path_to_file = "/Users/brandold/werkplace/solutions/efs-file-manager/test/e2e/run_e2e.sh"


@pytest.fixture
def browser():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    browser = webdriver.Chrome(chrome_options=chrome_options)
    return browser

def test_complete_app(browser):
    browser.implicitly_wait(5)
    browser.get("https://d3g24gya3qtb0w.cloudfront.net")

    # Login

    username_field = browser.find_element_by_xpath("/html/body/div/div[2]/div/div/div/div/div/div[2]/div[1]/div/input")
    username_field.send_keys("brandold@amazon.com")
    password_field = browser.find_element_by_xpath("/html/body/div/div[2]/div/div/div/div/div/div[2]/div[2]/input")
    password_field.send_keys("DtP90x!b")
    browser.find_element_by_xpath("/html/body/div/div[2]/div/div/div/div/div/div[3]/span/button").click()
    
    
    # Open file manager lambda creation page

    filesystem_element = browser.find_element_by_xpath("/html/body/div/div[2]/div/div/div/div/div/div/table/tbody/tr[1]/td[3]/div/p")

    assert filesystem_element.text == "fs-970b9692"
   
    browser.find_element_by_xpath("/html/body/div/div[2]/div/div/div/div/div/div/table/tbody/tr[1]/td[2]/div/a").click()
   
    # Click file manager lambda submit button
   
    browser.find_element_by_xpath("/html/body/div/div[2]/div/div/div/div[1]/form/button").click()
    
    # Wait for lambda to be created

    time.sleep(300)

    browser.refresh()

    # Open filesystem page
    browser.find_element_by_xpath("/html/body/div/div[2]/div/div/div/div/div/div/table/tbody/tr[1]/td[3]/div/a").click()
    

    # Create directory
    
    browser.find_element_by_xpath("/html/body/div/div[2]/div/div/div[1]/div/div/div/div[3]/button").click()
    mkdir_input = browser.find_element_by_xpath("/html/body/div[2]/div[1]/div/div/div/div/div/div/div/form/input")
    mkdir_input.send_keys(str(time.time()).split('.')[0])

    browser.find_element_by_xpath("/html/body/div[2]/div[1]/div/div/div/div/div/div/div/form/button").click()
    
    time.sleep(3)

    Alert(browser).accept()

    browser.find_element_by_xpath("/html/body/div[2]/div[1]/div/div/header/button").click()

    # Upload file

    browser.find_element_by_xpath("/html/body/div/div[2]/div/div/div[2]/div/div/div[1]/div[2]/button").click()
    
    browser.find_element_by_xpath("/html/body/div[2]/div[1]/div/div/div/div/div/div/div/div[1]/div/input").send_keys(path_to_file)
    
    time.sleep(3)

    browser.find_element_by_xpath("/html/body/div[2]/div[1]/div/div/div/div/div/div/div/div[2]/button").click()
    
    time.sleep(5)

    # Download file
    browser.find_element_by_xpath("/html/body/div/div[2]/div/div/div[2]/div/div/div[2]/table/tbody/tr/td/div/div[3]/a").click()

    time.sleep(5)

    # Delete file
    browser.find_element_by_xpath("/html/body/div/div[2]/div/div/div[2]/div/div/div[2]/table/tbody/tr/td/div/div[2]/a").click()

    time.sleep(3)

    Alert(browser).accept()

    # Sign out
    browser.find_element_by_xpath("/html/body/div/div[1]/nav/ul[2]/div/div/button").click()