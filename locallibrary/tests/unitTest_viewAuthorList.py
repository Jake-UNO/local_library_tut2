# Unit test file to determine if the Author List page is displayed when the user
# clicks the 'All Authors' button in the navigation pane of the local library
# application

import unittest
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

class ll_ATS(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Chrome()

    def test_ll(self):
        driver = self.driver
        driver.maximize_window()
        user = "testuser"
        pwd = "test1234"
        driver.get("http://127.0.0.1:8000/admin")
        time.sleep(3)
        elem = driver.find_element(By.ID, "id_username")
        elem.send_keys(user)
        elem = driver.find_element(By.ID, "id_password")
        elem.send_keys(pwd)
        time.sleep(3)
        elem.send_keys(Keys.RETURN)
        driver.get("http://127.0.0.1:8000")
        time.sleep(3)

        # find 'All Authors' and click it
        driver.find_element(By.LINK_TEXT, "All Authors").click()

        time.sleep(5)
        try:
            # verify Author List exists on new screen after clicking "All Authors" button
            elem = driver.find_element(By.LINK_TEXT, "Edit Author")
            self.driver.close()
            assert True

        except NoSuchElementException:
            driver.close()
            self.fail("Author List does not appear when All Authors clicked")

        time.sleep(2)

    def tearDown(self):
        self.driver.quit()


if __name__ == "__main__":
    unittest.main()