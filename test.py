from selenium import webdriver
from selenium.webdriver.firefox.options import Options
firefox_args = Options()
firefox_args.add_argument("-headless")
firefox_args.add_argument("-start-maximized")
firefox_args.add_argument("-profile")
firefox_args.add_argument("/Users/eric/Library/Application Support/Firefox/Profiles/6md6tbk9.SELENIUM")
driver = webdriver.Firefox(options=firefox_args)
driver.get("https://reddit.com")
driver.get_screenshot_as_file("screenshot.png")
driver.quit()
