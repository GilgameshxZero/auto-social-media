from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium import common
import selenium
import time
import fullscroll as fs
import logging

def ReactElement(driver, element, react, reacthoverwait):
	# scroll to element and hover
	driver.execute_script('arguments[0].scrollIntoView(false);', element)

	# scroll the element to the middle of page
	driver.execute_script('window.scrollBy(0, window.innerHeight / 2);')
	actions = selenium.webdriver.common.action_chains.ActionChains(driver)
	actions.move_to_element(element)
	actions.perform()

	time.sleep(float(reacthoverwait))

	# get element of correct reaction and perform
	actions = selenium.webdriver.common.action_chains.ActionChains(driver)
	reactbutton = None
	toolbarparlist = driver.find_elements_by_css_selector('div[aria-label="Reactions"]')
	toolbarpar = toolbarparlist[-1]
	for a in range(len(toolbarparlist)):
		if toolbarparlist[a].is_displayed():
			toolbarpar = toolbarparlist[a]
			break
	if react == 'like':
		reactbutton = toolbarpar.find_element_by_css_selector('span[aria-label="Like"]')
	elif react == 'angry':
		reactbutton = toolbarpar.find_element_by_css_selector('span[aria-label="Angry"]')
	elif react == 'love':
		reactbutton = toolbarpar.find_element_by_css_selector('span[aria-label="Love"]')
	elif react == 'sad':
		reactbutton = toolbarpar.find_element_by_css_selector('span[aria-label="Sad"]')
	elif react == 'haha':
		reactbutton = toolbarpar.find_element_by_css_selector('span[aria-label="Haha"]')
	elif react == 'wow':
		reactbutton = toolbarpar.find_element_by_css_selector('span[aria-label="Wow"]')
	actions.click(reactbutton)
	actions.perform()
		
# autolike fb posts based on parameters
def AutoFB (params, logger):
	# inititialize parameters
	pageloadwait = float(params['fb-pageloadwait'])
	scrollwait = float(params['fb-scrollwait'])
	reactcooldown = float(params['fb-reactcooldown'])
	frlinks = []
	if params['fb-friendprofiles'] != 'All':
		f = open(params['fb-friendprofiles'], 'r')
		for a in f:
			frlinks.append('https://www.facebook.com/' + a.strip())
		f.close()

	# start driver and login to fb
	logger.info('INFO: logging in')

	chrome_options = Options()
	chrome_options.add_argument('--disable-notifications')
	if params['hideBrowser'] == 'yes':
		chrome_options.add_argument('--headless')
	driver = webdriver.Chrome(params['chromedrloc'], chrome_options=chrome_options)
	driver.get('https://www.facebook.com/login.php')
	time.sleep(pageloadwait)
	driver.find_element_by_id('email').send_keys(params['fb-username'])
	driver.find_element_by_id('pass').send_keys(params['fb-password'])
	driver.find_element_by_id('loginbutton').click()
	time.sleep(pageloadwait)

	logger.info('SUCCESS: login success')

	# react posts from the feed
	logger.info('INFO: reacting feed for a max of ' + params['fb-feedreactlimit'] + ' reacts')

	reacts = 0
	curheight = 0
	windowheight = driver.execute_script('return window.innerHeight || document.documentElement.clientHeight || document.body.clientHeight')
	while reacts < int(params['fb-feedreactlimit']):
		driver.execute_script('window.scrollTo(0, arguments[0]);', curheight)
		time.sleep(scrollwait)
		curheight += windowheight

		buttons = driver.find_elements_by_css_selector('a[data-testid="fb-ufi-likelink"]')
		for a in range(len(buttons)):
			if buttons[a].is_displayed():
				ReactElement(driver, buttons[a], params['fb-react'], params['fb-reacthoverwait'])
				reacts += 1
				logger.info('SUCCESS: ' + str(reacts) + ' reacts')
				time.sleep(reactcooldown)

	logger.info('INFO: finished reacting from the feed')
	
	# get links to friend profiles
	logger.info('INFO: getting friend profile links')

	if params['fb-friendprofiles'] == 'All':
		driver.get('https://www.facebook.com/me')
		friendsurl = driver.find_element_by_css_selector('a[data-tab-key="friends"]').get_attribute('href')
		time.sleep(pageloadwait)
		driver.get(friendsurl)
		time.sleep(pageloadwait)

		fs.FullScroll(driver, pausetime=scrollwait)
		friends = driver.find_elements_by_css_selector('div[class="uiProfileBlockContent"]')
		for a in range(len(friends)):
			frlinks.append(friends[a].find_element_by_tag_name('a').get_attribute('href'))
		logger.info('INFO: found ' + str(len(frlinks)) + ' friends from friends list')
	else:
		logger.info('INFO: found ' + str(len(frlinks)) + ' friends from optional file')
	
	# react posts from friend walls
	logger.info('INFO: reacting friend wall posts')

	totalreacts = 0
	for a in range(len(frlinks)):
		driver.get(frlinks[a])
		time.sleep(pageloadwait)
		name = driver.find_element_by_id('fb-timeline-cover-name').find_element_by_tag_name('a').get_attribute('innerHTML')

		reacts = 0
		curheight = 0
		windowheight = driver.execute_script('return window.innerHeight || document.documentElement.clientHeight || document.body.clientHeight')
		while reacts < int(params['fb-friendreactlimit']):
			driver.execute_script('window.scrollTo(0, arguments[0]);', curheight)
			time.sleep(scrollwait)
			curheight += windowheight

			buttons = driver.find_elements_by_css_selector('a[data-testid="fb-ufi-likelink"]')
			for a in range(len(buttons)):
				if buttons[a].is_displayed():
					ReactElement(driver, buttons[a], params['fb-react'], params['fb-reacthoverwait'])
					reacts += 1
					logger.info('SUCCESS: ' + name + ': ' + str(reacts) + ' reacts')
					time.sleep(reactcooldown)

		totalreacts += reacts

	logger.info('SUCCESS: finished: ' + str(totalreacts) + ' reacts total')

	# clean up
	driver.get('https://www.facebook.com/me') # give window time to close
	driver.close()