#!/usr/bin/python

# Created on: 2015.03.XX 
# Author: Carlo Artieri

##############################
# HISTORY AND THINGS TO FIX  #
##############################
#2015.04.02 - Updated script to use argparse and added option to exclude local-specific 
#			  module imports
#2015.04.10 - Added default import of subprocess and fixed how argparse commands were being
#			  printed.
#2015.04.16 - Added import of numpy and os modules. Tweaked output of base script.

###########
# MODULES #
###########

import sys			#Provides access to simple command-line arguments
sys.path.append('/Users/carloartieri/bin/python')
import getopt		#Provides access to long-form command-line arguments
import re			#Provides access to REGEX splitting
import common		#My custom common python scripts
import argparse
import datetime

##########################
# COMMAND-LINE ARGUMENTS #
##########################

parser = argparse.ArgumentParser(description='Initialize a Python script with default modules/settings', add_help=False)
req = parser.add_argument_group('Required arguments:')
req.add_argument('-f','--file', action="store", dest="outfile", help='Name of script to create', required=True, metavar='')
#req.add_argument('-c','--cols', action="store", dest="colstep", help='1-based start column and step', nargs=2, required=True, metavar=('COL','STEP'))
opt = parser.add_argument_group('Optional arguments:')
opt.add_argument('-d','--disable', action="store_true", dest="dis", help='Disable local-specific module calls')
opt.add_argument('-h', '--help', action="help", help="show this help message and exit")
args = parser.parse_args()

#############
# FUNCTIONS #
#############

##########
# SCRIPT #
##########

#Get the current date
now = datetime.datetime.now()
curr_date = str(now.year) + '.' + str("%02d" % (now.month,)) + '.' + str("%02d" % (now.day,))

if args.dis == True:
	local = ''
else:	#Set local-specific module calls here
	local = """sys.path.append('/Users/carloartieri/bin/python') #Set python path for common functions
import common		#My custom common python scripts"""

script_header = """\
#!/usr/bin/python

# Created on: """ + curr_date + """ 
# Author: Carlo Artieri

##############################
# HISTORY AND THINGS TO FIX  #
##############################
#""" + curr_date + """ - Initial script

###########
# MODULES #
###########
import sys			#Access to simple command-line arguments
import argparse		#Access to long command-line parsing	
import datetime		#Access to calendar/clock functions
import re			#Access to REGEX splitting
import math			#Access to math functions
import subprocess	#Access to shell commands
import os			#Access to shell commands (old)
import numpy		#Access to numerical python functions
import random		#Access to random number generator\n""" + local + """

##########################
# COMMAND-LINE ARGUMENTS #
##########################

parser = argparse.ArgumentParser(description='[PROGRAM DESCRIPTION]', add_help=False)
req = parser.add_argument_group('Required arguments:')
req.add_argument('-i','--infile', action='store', dest='infile', help='Input table', required=True, metavar='')
req.add_argument('-o','--outfile', action='store', dest='outfile', help='Zipped output table', required=True, metavar='')
#req.add_argument('-c','--cols', action='store', dest='colstep', help='1-based start column and step', nargs=2, required=True, metavar=('COL','STEP'))
opt = parser.add_argument_group('Optional arguments:')
opt.add_argument('-h', '--help', action='help', help='show this help message and exit')
args = parser.parse_args()

#############
# FUNCTIONS #
#############

##########
# SCRIPT #
##########

infile = open(FILE, 'r')
for line in infile:

	line = line.rstrip('\\n')
	line_t = line.split('\\t')

"""

#Open up a file and write the default python script header
script = open(args.outfile, "w")
script.write(script_header)
script.close()

