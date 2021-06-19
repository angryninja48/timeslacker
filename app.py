import os
from time import sleep
# from selenium.webdriver import Firefox
# from selenium.webdriver.firefox.options import Options
from selenium.webdriver import Chrome
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

TIME_SHEET_URL = os.getenv("TIME_SHEET_URL")
TIME_SHEET_FIELD = {
    'Monday': 'monDay',
    'Tuesday': 'tueDay',
    'Wednesday': 'wedDay',
    'Thursday': 'thuDay',
    'Friday': 'friDay',
    'Saturday': 'satDay',
    'Sunday': 'sunDay'
}

class TimeSheet:
    def __init__(self, username, password, days=None, non_worked_days=None, headless=True):
    
        self.username = username
        self.password = password
        self.days = days
        self.non_worked_days = non_worked_days
        self.browser_timeout_seconds = 10
        self.headless = headless

        if self.headless:
            opt = ChromeOptions()
            opt.add_argument('--headless')
            opt.add_argument('--no-sandbox')
            opt.add_argument('--disable-dev-shm-usage')
            self.browser = Chrome(options=opt) 

        else:
            self.browser = Chrome()

        if not self.days:
            self.days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        
        if not self.non_worked_days:
            self.non_worked_days = ['Saturday', 'Sunday']

    def wait(self):
        return WebDriverWait(self.browser, 20)

    def implicitlywait(self):
        return self.browser.implicitly_wait(self.browser_timeout_seconds)

    def close(self):
        return self.browser.quit()

    def login(self):
        self.browser.get(TIME_SHEET_URL)
        # self.wait().until(EC.presence_of_element_located((By.XPATH, "//*[@id='j_username']")))

        self.wait().until(EC.title_contains("skillstream"))
        print(f'Title: {self.browser.title}')

        try:
            self.browser.find_element_by_id("username").send_keys(self.username)
            self.browser.find_element_by_id("password").send_keys(self.password)
            self.browser.find_element_by_id("submit").click()
        except:
            pass # Add in better exception handling

        if self.browser.current_url == f'{TIME_SHEET_URL}/twg/login?login_error=1':
            print('Username and/or Passowrd incorrect') 
        else:
            print('Login Successful') 
            sleep(3)

    def logout(self):
        self.browser.find_element_by_xpath("//a[@href='/twg/j_spring_security_logout']")
        print('Logout Successful')
        self.close()


    def fill_timesheet(self):
        # self.wait().until(EC.presence_of_element_located((By.XPATH, "//*[@id='monDay']")))
        # self.implicitlywait()
        self.wait().until(EC.presence_of_element_located((By.ID, "navigation-bar")))

        # Fill worked days
        for day in self.days:
            self.browser.find_element_by_id(TIME_SHEET_FIELD[day]).clear()
            self.browser.find_element_by_id(TIME_SHEET_FIELD[day]).send_keys("1")    

        # Fill non working days
        for day in self.non_worked_days:
            # build leave id string
            leaveid =  f"{day.lower()[0:3]}Leave"
            leavetype =  f"{leaveid}Type"

            # Clear field
            self.browser.find_element_by_id(TIME_SHEET_FIELD[day]).clear()
            self.browser.find_element_by_id(TIME_SHEET_FIELD[day]).send_keys("0")
            # Select full day leave
            select = Select(self.browser.find_element_by_id(leaveid))
            select.select_by_value('1.0')
            # Select reason as standard non working day
            select = Select(self.browser.find_element_by_id(leavetype))
            select.select_by_value('6')

        # Click disclaimer
        # self.browser.find_element_by_id("ts_disclaimer_1").click()
        disclaimer = self.browser.find_element_by_xpath("//input[@id='ts_disclaimer_1' and @type='checkbox']")
        self.browser.execute_script("arguments[0].click();", disclaimer)
        if self.browser.find_element_by_id("ts_disclaimer_1").is_selected():
            print('Timesheet Checkbox clicked!') 
        else:
            print('Timesheet Entry Failed')

    def submit(self):
        # 1st Submit
        # submit = self.browser.find_element_by_xpath("//input[@type='submit' and @value='submit']")
        # submit.click()
        submit = self.browser.find_element_by_xpath("//input[@type='submit' and @value='submit']")
        self.browser.execute_script("arguments[0].click();", submit)

        # Wait for next page
        self.wait().until(EC.presence_of_element_located((By.XPATH, "//input[@type='submit' and @value='submit to manager']")))
        # Confirm
        sub_to_man = self.browser.find_element_by_xpath("//input[@type='submit' and @value='submit to manager']")
        self.browser.execute_script("arguments[0].click();", sub_to_man)

    def run(self):
        self.login()
        self.fill_timesheet()
        self.submit()
        self.close()
        # self.logout() # logout doesn't work

