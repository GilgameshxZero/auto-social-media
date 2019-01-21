from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium import common
import selenium
import time
import logging

import rain

def reactFacebookPost(driver, element, react, reacthoverwait):
	# scroll to element and hover
	driver.execute_script("arguments[0].scrollIntoView(false);", element)
	time.sleep(2)

	# scroll the element to the middle of page
	driver.execute_script("window.scrollBy(0, window.innerHeight / 2);")
	time.sleep(2)

	#hover element
	actions = selenium.webdriver.common.action_chains.ActionChains(driver)
	actions.move_to_element(element)
	actions.perform()
	time.sleep(float(reacthoverwait))

	# get element of correct reaction and perform
	actions = selenium.webdriver.common.action_chains.ActionChains(driver)
	toolbarparlist = driver.find_elements_by_css_selector("div[aria-label=\"Reactions\"]")
	toolbarpar = toolbarparlist[-1]
	for a in range(len(toolbarparlist)):
		if toolbarparlist[a].is_displayed():
			toolbarpar = toolbarparlist[a]
			break
	
	ariaLabel = react.capitalize()
	reactbutton = toolbarpar.find_element_by_css_selector("span[aria-label=" + ariaLabel + "]")
	actions.click(reactbutton)
	actions.perform()
		
# autolike fb posts based on parameters
def manageFacebook (params, logger):
	# inititialize parameters
	pageloadwait = float(params["fb-pageloadwait"])
	scrollwait = float(params["fb-scrollwait"])
	reactcooldown = float(params["fb-reactcooldown"])
	frlinks = []
	if params["fb-friendprofiles"] != "All":
		f = open(rain.toRelPath(params["fb-friendprofiles"]), "r")
		for a in f:
			frlinks.append("https://www.facebook.com/" + a.strip())
		f.close()

	# start driver and login to fb
	logger.info("INFO: logging in")

	chrome_options = Options()
	chrome_options.add_argument("--disable-notifications --mute-audio --log-level=3 --silent")
	if params["hideBrowser"] == "yes":
		chrome_options.add_argument("--headless")
	driver = webdriver.Chrome(rain.toRelPath(params["chromedrloc"]), chrome_options=chrome_options)
	driver.implicitly_wait(0) #blocks for pages to load

	driver.get("https://www.facebook.com/login.php")
	driver.find_element_by_id("email").send_keys(params["fb-username"])
	driver.find_element_by_id("pass").send_keys(params["fb-password"])
	driver.find_element_by_id("loginbutton").click()

	logger.info("SUCCESS: login success")

	# react posts from the feed
	logger.info("INFO: reacting feed for a max of " + params["fb-feedreactlimit"] + " reacts")

	reacts = 0
	curheight = 0
	windowHeight = driver.execute_script("return window.innerHeight || document.documentElement.clientHeight || document.body.clientHeight;")
	while reacts < int(params["fb-feedreactlimit"]):
		driver.execute_script("window.scrollTo(0, arguments[0]);", curheight)
		curheight += windowHeight

		#TODO: better wait
		time.sleep(scrollwait)

		buttons = driver.find_elements_by_css_selector("a[data-testid=\"fb-ufi-likelink\"]")
		for a in range(len(buttons)):
			if buttons[a].is_displayed():
				#reset scroll so that the element is always beneath us
				driver.execute_script("window.scrollTo(0, 0);")
				reactFacebookPost(driver, buttons[a], params["fb-react"], params["fb-reacthoverwait"])

				reacts += 1
				logger.info("SUCCESS: " + str(reacts) + " reacts")
				time.sleep(reactcooldown)

	logger.info("INFO: finished reacting from the feed")
	
	# get links to friend profiles
	logger.info("INFO: getting friend profile links")

	if params["fb-friendprofiles"] == "All":
		driver.get("https://www.facebook.com/me")
		friendsurl = driver.find_element_by_css_selector("a[data-tab-key=\"friends\"]").get_attribute("href")
		time.sleep(pageloadwait)
		driver.get(friendsurl)
		time.sleep(pageloadwait)

		rain.seleniumFullScroll(driver, pausetime=scrollwait)
		friends = driver.find_elements_by_css_selector("div[class=\"uiProfileBlockContent\"]")
		for a in range(len(friends)):
			frlinks.append(friends[a].find_element_by_tag_name("a").get_attribute("href"))
		logger.info("INFO: found " + str(len(frlinks)) + " friends from friends list")
	else:
		logger.info("INFO: found " + str(len(frlinks)) + " friends from optional file")
	
	# react posts from friend walls
	logger.info("INFO: reacting friend wall posts")

	totalreacts = 0
	for a in range(len(frlinks)):
		driver.get(frlinks[a])
		time.sleep(pageloadwait)
		name = driver.find_element_by_id("fb-timeline-cover-name").find_element_by_tag_name("a").get_attribute("innerHTML")

		reacts = 0
		curheight = 0
		windowHeight = driver.execute_script("return window.innerHeight || document.documentElement.clientHeight || document.body.clientHeight")
		while reacts < int(params["fb-friendreactlimit"]):
			driver.execute_script("window.scrollTo(0, arguments[0]);", curheight)
			time.sleep(scrollwait)
			curheight += windowHeight

			buttons = driver.find_elements_by_css_selector("a[data-testid=\"fb-ufi-likelink\"]")
			for a in range(len(buttons)):
				if buttons[a].is_displayed():
					reactFacebookPost(driver, buttons[a], params["fb-react"], params["fb-reacthoverwait"])

					reacts += 1
					logger.info("SUCCESS: " + name + ": " + str(reacts) + " reacts")
					time.sleep(reactcooldown)

		totalreacts += reacts

	logger.info("SUCCESS: finished: " + str(totalreacts) + " reacts total")

	# clean up
	driver.get("https://www.facebook.com/me") # give window time to close
	driver.close()

# autolike instagram posts based on parameters
def manageInsta (params, logger):
	# inititialize parameters
	pageloadwait = float(params["insta-pageloadwait"])
	scrollwait = float(params["insta-scrollwait"])
	heartcooldown = float(params["insta-heartcooldown"])

	# login
	logger.info("INFO: logging in")

	chrome_options = Options()
	chrome_options.add_argument("--disable-notifications --mute-audio --log-level=3 --silent")
	if params["hideBrowser"] == "yes":
		chrome_options.add_argument("--headless")
	driver = webdriver.Chrome(rain.toRelPath(params["chromedrloc"]), chrome_options=chrome_options)
	driver.implicitly_wait(0) #blocks for pages to load

	driver.get("https://www.instagram.com/")
	driver.find_element_by_link_text("Log in").click()
	time.sleep(pageloadwait)
	driver.find_element_by_name("username").send_keys(params["insta-username"])
	driver.find_element_by_name("password").send_keys(params["insta-password"])
	driver.find_element_by_xpath("//button[text()=\"Log in\"]").click()

	logger.info("SUCCESS: login success")

	# scoll pages and heart posts until many current pages contain no more hearts
	logger.info("INFO: hearting posts")

	curheight = 0
	totalhearts = 0
	nohearts = 0
	windowHeight = driver.execute_script("return window.innerHeight || document.documentElement.clientHeight || document.body.clientHeight")
	while nohearts <= int(params["insta-noheartlimit"]):
		driver.execute_script("window.scrollTo(0, arguments[0]);", curheight)
		curheight += windowHeight
		time.sleep(scrollwait)

		hearts = driver.find_elements_by_class_name("coreSpriteHeartOpen")

		clicked = False

		for a in range(len(hearts)):
			if hearts[a].is_displayed():
				#only if the child element has aria-label "Like"
				unlikeChilds = hearts[a].find_elements_by_css_selector("span[aria-label=\"Unlike\"]")
				print(unlikeChilds)
				if len(unlikeChilds) > 0:
					continue

				# scroll element into the middle of page
				driver.execute_script("window.scrollBy(0, arguments[0]);", driver.execute_script("return arguments[0].getBoundingClientRect().top;", hearts[a]) - windowHeight / 2)

				hearts[a].click()
				totalhearts += 1
				logger.info("SUCCESS: " + str(totalhearts) + " hearts")
				clicked = True
				time.sleep(heartcooldown)

		if clicked:
			nohearts = 0
		else:
			nohearts += 1
			
	logger.info("INFO: no more hearts found")

	# clean up
	driver.get("https://www.instagram.com/") # to give window time to close
	driver.close()