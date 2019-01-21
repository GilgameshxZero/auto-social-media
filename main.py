import components
import logging

import rain

# inititialize parameters
print("INFO: reading configuration file...")

try:
	f = open(rain.toRelPath("config.ini"), "r")
except FileNotFoundError:
	input("ERROR: configuration file not found")
	exit()
params = {}
for line in f:
	if len(line.strip()) == 0:
		continue
	linesplit = line.strip().split(sep = None, maxsplit = 1)
	params[linesplit[0]] = linesplit[1]
f.close()

try:
	f = open(rain.toRelPath(params["credentials"]), "r")
except FileNotFoundError:
	input("ERROR: " + params["credentials"] + " configuration file not found")
	exit()
for line in f:
	if len(line.strip()) == 0:
		continue
	linesplit = line.strip().split(sep = None, maxsplit = 1)
	params[linesplit[0]] = linesplit[1]
f.close()

print("SUCCESS: done reading configuration file")
print(params)

# set up logging
logger = logging.getLogger("log")
logger.setLevel(logging.DEBUG)
file_log_handler = logging.FileHandler(params["logfile"], mode = "a")
stream_log_handler = logging.StreamHandler()
file_log_handler.setLevel(logging.DEBUG)
stream_log_handler.setLevel(logging.DEBUG)
logger.addHandler(file_log_handler)
logger.addHandler(stream_log_handler)
formatter = logging.Formatter("%(asctime)s - %(message)s")
file_log_handler.setFormatter(formatter)
stream_log_handler.setFormatter(formatter)

# run components
logger.info("INFO: running components")
component = {"fb": components.manageFacebook, 
			"insta": components.manageInsta}
for key in component:
	if key in params["component"]:
		logger.info("INFO: running " + key)
		try:
			component[key](params, logger)
			logger.info("SUCCESS: finished " + key)
		except:
			logger.info("FAILURE")
logger.info("SUCCESS: finished")