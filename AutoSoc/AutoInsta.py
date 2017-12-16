from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time
import fullscroll as fs
import logging

# autolike insta posts based on parameters
def AutoInsta (params, logger):
	# inititialize parameters
	logger.info('INFO: reading insta parameters')
	loadtime = int(params['insta-loadtime'])
	scrollwait = int(params['insta-scrollwait'])
	likecd = int(params['insta-likecd'])
	sclim = int(params['insta-sclim'])
	logger.info('SUCCESS: insta parameters read success')

	# login
	logger.info('INFO: logging into insta')
	chrome_options = Options()
	chrome_options.add_argument("--disable-notifications")
	driver = webdriver.Chrome(params['chromedrloc'], chrome_options=chrome_options)

	driver.get('https://www.instagram.com/')
	time.sleep(loadtime)
	driver.find_element_by_link_text('Log in').click()
	time.sleep(loadtime)
	driver.find_element_by_css_selector('input[aria-label="Phone number, username, or email"]').send_keys(params['insta-username'])
	driver.find_element_by_css_selector('input[aria-label="Password"]').send_keys(params['insta-password'])
	driver.find_element_by_css_selector('button[class="_qv64e _gexxb _4tgw8 _njrw0"]').click()
	time.sleep(loadtime)
	logger.info('SUCCESS: insta login success')

	# load all posts we want to heart
	fs.FullScroll(driver, pausetime=scrollwait, limit=sclim) 

	# heart all posts by scrolling through page
	logger.info('INFO: liking posts')

	totalheight = driver.execute_script('return document.body.scrollHeight')
	windowheight = driver.execute_script('return window.innerHeight || document.documentElement.clientHeight || document.body.clientHeight')
	
	curheight = 0
	likestotal = 0
	while curheight < totalheight:
		driver.execute_script('window.scrollTo(0, arguments[0]);', curheight)
		curheight += windowheight
		likebuttons = driver.find_elements_by_class_name('coreSpriteHeartOpen')
		for a in range(len(likebuttons)):
			if likestotal >= int(params['insta-likelim']):
				break
			driver.execute_script('arguments[0].parentNode.click()', likebuttons[a])
			likestotal += 1
			logger.info('INFO: ' + str(likestotal) + ' likes')
			time.sleep(likecd)		
	logger.info('SUCCESS: finished; ' + str(likestotal) + ' likes total')

	# clean up
	driver.get('https://www.instagram.com/') # to give window time to close
	driver.close()