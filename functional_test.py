from selenium import webdriver
import unittest


class DjangoTest(unittest.TestCase):
    def setUp(self):
        self.browser = webdriver.Chrome(
            "/Users/dhfpt/Desktop/chromedriver_win32/chromedriver"
        )
        self.browser.implicitly_wait(3)

    def tearDown(self):
        self.browser.quit()

    # def test_can_start_a_user_and_retrieve_it_later(self):
    #     self.browser.get('http://localhost:8000/user')

    #     self.assertIn('User', self.browser.title)
    #     self.fail('Finish the test!')


if __name__ == "__main__":
    unittest.main()
