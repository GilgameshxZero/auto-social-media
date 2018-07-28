import os
import selenium
import time

def toRelPath(origPath):
	"""Converts path to path relative to current script

	origPath:	path to convert
	"""
	try:
		if not hasattr(toRelPath, "__location__"):
			toRelPath.__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
		return os.path.join(toRelPath.__location__, origPath)
	except NameError:
		return origPath
	
def getMBUsage():
	process = psutil.Process(os.getpid())
	return process.memory_info().rss / 1e6

def setCUDAVisible(devices):
	"""
	0: 1080Ti, 1: 940MX
	"""
	os.environ["CUDA_VISIBLE_DEVICES"] = devices
	
def seleniumFullScroll (driver, pausetime=1, limit=0):
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
