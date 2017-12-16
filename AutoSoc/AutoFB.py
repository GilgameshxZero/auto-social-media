from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium import common
import selenium
import time
import fullscroll as fs
import logging
		
# autolike fb posts based on parameters
def AutoFB (params, logger):
	# inititialize parameters
	logger.info('INFO: reading fb parameters')
	loadtime = int(params['fb-pageloadwait'])
	scrollwait = int(params['fb-scrollwait'])
	wallsclim = int(params['fb-wallscrolllim'])
	likecd = int(params['fb-reactcooldown'])
	likelim = int(params['fb-friendreactlim'])
	frlinks = []
	if params['fb-friendprofiles'] != 'All':
		f = open(params['fb-friendprofiles'], 'r')
		for a in range(int(params['fb-fileprofilecnt'])):
			frlinks.append(f.readline().strip())
		f.close()
	logger.info('SUCCESS: fb parameters read success')

	# start driver and login to fb
	logger.info('INFO: logging into fb')
	chrome_options = Options()
	chrome_options.add_argument("--disable-notifications")
	driver = webdriver.Chrome(params['chromedrloc'], chrome_options=chrome_options)

	driver.get('https://www.facebook.com/login.php')
	time.sleep(loadtime)
	driver.find_element_by_id('email').send_keys(params['fb-username'])
	driver.find_element_by_id('pass').send_keys(params['fb-password'])
	time.sleep(loadtime)
	driver.find_element_by_id('loginbutton').click()
	time.sleep(loadtime)
	logger.info('SUCCESS: fb login success')

	if params['fb-mode'] == 'feed':
		# like at most fb-feedreactlim posts from the feed
		logger.info('INFO: liking feed posts; MAX: ' + params['fb-feedreactlim'])
		fs.FullScroll(driver, pausetime=scrollwait, limit=int(params['fb-feedscrolllim']))
		likebuttons = driver.find_elements_by_css_selector('a[data-testid="fb-ufi-likelink"]')
		
		actuallikes = 0
		for a in range(len(likebuttons)):
			if actuallikes >= int(params['fb-feedreactlim']):
				break
			if likebuttons[a].get_attribute('data-testid') == 'fb-ufi-likelink': # sometimes videos have two like buttons, but don't want to doubleclick
				driver.execute_script('arguments[0].click()', likebuttons[a])
				actuallikes += 1
				logger.info('INFO: ' + str(actuallikes) + ' of ' + str(len(likebuttons) - a + actuallikes - 1) + ' reacts')
				time.sleep(likecd)
		logger.info('SUCCESS: finished: ' + str(actuallikes) + ' reacts total')
	elif params['fb-mode'] == 'friend':
		# get all links to friend profiles
		logger.info('INFO: getting friend profile links')
		if params['fb-friendprofiles'] == 'All':
			driver.get('https://www.facebook.com/me')
			friendsurl = driver.find_element_by_css_selector('a[data-tab-key="friends"]').get_attribute('href')
			time.sleep(loadtime)
			driver.get(friendsurl)
			time.sleep(loadtime)

			fs.FullScroll(driver, pausetime=scrollwait)
			friends = driver.find_elements_by_css_selector('a[class="_5q6s _8o _8t lfloat _ohe"]')
			for a in range(len(friends)):
				frlinks.append(friends[a].get_attribute('href'))
			logger.info('SUCCESS: found ' + str(len(frlinks)) + ' friends in friends list')
		else:
			logger.info('SUCCESS: found ' + str(len(frlinks)) + ' friends in optional file file')
	
		# like posts
		logger.info('INFO: reacting posts')
		totallikes = 0
		flag = False
		for a in range(len(frlinks)):
			driver.get(frlinks[a])
			time.sleep(loadtime)

			name = driver.find_element_by_css_selector('a[class="_2nlw _2nlv"]').get_attribute('innerHTML')

			fs.FullScroll(driver, pausetime=scrollwait, limit=wallsclim)

			# get all like buttons regardless if pressed
			likebuttons = driver.find_elements_by_css_selector('a[data-testid="fb-ufi-likelink"]')
			likebuttons.extend(driver.find_elements_by_css_selector('a[data-testid="fb-ufi-unlikelink"]'))

			personlikes = 0

			for b in range(len(likebuttons)):
				if likelim != 0 and personlikes >= likelim:
					break

				# scroll to element and hover
				actions = selenium.webdriver.common.action_chains.ActionChains(driver)
				actions.move_to_element(likebuttons[b])
				actions.perform()

				driver.execute_script('arguments[0].scrollIntoView(false);', likebuttons[b])
				driver.execute_script('window.scrollBy(0, window.innerHeight / 2);')
				actions = selenium.webdriver.common.action_chains.ActionChains(driver)
				actions.move_to_element(likebuttons[b])
				actions.perform()

				time.sleep(float(params['fb-reacthoverwait']))

				# get element of correct reaction and perform
				actions = selenium.webdriver.common.action_chains.ActionChains(driver)
				reactbutton = None
				toolbarpar = driver.find_element_by_css_selector('div[class="_1oxj uiLayer"]')
				if params['fb-react'] == 'like':
					reactbutton = toolbarpar.find_element_by_css_selector('span[aria-label="Like"]')
				elif params['fb-react'] == 'angry':
					reactbutton = toolbarpar.find_element_by_css_selector('span[aria-label="Angry"]')
				elif params['fb-react'] == 'love':
					reactbutton = toolbarpar.find_element_by_css_selector('span[aria-label="Love"]')
				elif params['fb-react'] == 'sad':
					reactbutton = toolbarpar.find_element_by_css_selector('span[aria-label="Sad"]')
				elif params['fb-react'] == 'haha':
					reactbutton = toolbarpar.find_element_by_css_selector('span[aria-label="Haha"]')
				actions.click(reactbutton)
				actions.perform()

				# logging
				personlikes += 1
				logger.info('INFO: ' + str(a) + ': ' + name + ': ' + str(personlikes) + ' of ' + str(len(likebuttons) - b + personlikes - 1) + ' reacts')

				# logistics
				time.sleep(likecd)

			totallikes += personlikes
		logger.info('SUCCESS: finished: ' + str(totallikes) + ' reacts total')

	# clean up
	driver.get('https://www.facebook.com/me') # to give window time to close
	driver.close()