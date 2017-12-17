from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time
import fullscroll as fs
import logging

# autolike instafeM posts based on parameters
def AutoInsta (params, logger):
	# inititialize parameters
	pageloadwait = float(params['insta-pageloadwait'])
	scrollwait = float(params['insta-scrollwait'])
	heartcooldown = float(params['insta-heartcooldown'])

	# login
	logger.info('INFO: logging in')

	chrome_options = Options()
	chrome_options.add_argument("--disable-notifications")
	driver = webdriver.Chrome(params['chromedrloc'], chrome_options=chrome_options)

	driver.get('https://www.instagram.com/')
	time.sleep(pageloadwait)
	driver.find_element_by_link_text('Log in').click()
	time.sleep(pageloadwait)
	driver.find_element_by_name('username').send_keys(params['insta-username'])
	driver.find_element_by_name('password').send_keys(params['insta-password'])
	driver.find_element_by_xpath("//button[text()='Log in']").click()
	time.sleep(pageloadwait)

	logger.info('SUCCESS: login success')

	# scoll pages and heart posts until many current pages contain no more hearts
	logger.info('INFO: hearting posts')

	curheight = 0
	totalhearts = 0
	nohearts = 0
	windowheight = driver.execute_script('return window.innerHeight || document.documentElement.clientHeight || document.body.clientHeight')
	while nohearts <= int(params['insta-noheartlimit']):
		driver.execute_script('window.scrollTo(0, arguments[0]);', curheight)
		time.sleep(scrollwait)
		curheight += windowheight
		hearts = driver.find_elements_by_class_name('coreSpriteHeartOpen')

		if len(hearts) == 0:
			nohearts += 1
		else:
			nohearts = 0

		for a in range(len(hearts)):
			if hearts[a].is_displayed():
				hearts[a].click()
				totalhearts += 1
				logger.info('SUCCESS: ' + str(totalhearts) + ' hearts')
				time.sleep(heartcooldown)
			
	logger.info('INFO: no more hearts found')

	# clean up
	driver.get('https://www.instagram.com/') # to give window time to close
	driver.close()