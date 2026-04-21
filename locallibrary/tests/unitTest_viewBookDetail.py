# Unit test file to determine if the Book Detail page is displayed when the user
# clicks a book title from the Book List page in the local library application

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

        # Login
        driver.get("http://127.0.0.1:8000/admin")
        time.sleep(3)
        elem = driver.find_element(By.ID, "id_username")
        elem.send_keys(user)
        elem = driver.find_element(By.ID, "id_password")
        elem.send_keys(pwd)
        time.sleep(2)
        elem.send_keys(Keys.RETURN)

        # Go to homepage
        driver.get("http://127.0.0.1:8000")
        time.sleep(3)

        # Click All Books
        driver.find_element(By.XPATH, "//a[contains(., 'All Books')]").click()
        time.sleep(3)

        # Click the first book title
        driver.find_element(By.XPATH, "(//ul/li/a)[1]").click()
        time.sleep(3)

        try:
            # Verify Book Detail page loaded by checking for title (h1)
            elem = driver.find_element(By.TAG_NAME, "h1")
            self.driver.close()
            assert True

        except NoSuchElementException:
            driver.close()
            self.fail("Book Detail page does not appear when a book title is clicked")

        time.sleep(2)

    def tearDown(self):
        self.driver.quit()


if __name__ == "__main__":
    unittest.main()