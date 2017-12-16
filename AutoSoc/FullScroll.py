from selenium import webdriver
import time

# fully scroll infinite page
def FullScroll (driver, pausetime=1, limit=0):
	last_height = driver.execute_script('return document.body.scrollHeight')
	times = 0
	while limit == 0 or times < limit:
		driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
		time.sleep(pausetime)
		new_height = driver.execute_script('return document.body.scrollHeight')
		if new_height == last_height:
			break
		last_height = new_height
		times += 1
