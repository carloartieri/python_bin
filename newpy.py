#!/usr/bin/python

###########
# MODULES #
###########

import sys			#Provides access to simple command-line arguments
sys.path.append('/Users/carloartieri/bin/python')
import getopt		#Provides access to long-form command-line arguments
import re			#Provides access to REGEX splitting
import common		#My custom common python scripts
import datetime

##########################
# COMMAND-LINE ARGUMENTS #
##########################

#For simple arguments where args[0] is argument 1, etc.
args = sys.argv	#sys.argv stores the command-line arguments
prog_name = args.pop(0)	#Remove the element at position 0 

#For long-form arguments
try:
	opts,args = getopt.getopt(args, "hf:",["help","file="])
except getopt.GetoptError:
	common.print_ansi('Usage:' + prog_name +' -f/--file [NEW PYTHON SCRIPT]', 'red')
	sys.exit(2)
for opt, arg in opts:                
	if opt in ("-h", "--help"):      
		common.print_ansi('Usage:' + prog_name +' -f/--file [NEW PYTHON SCRIPT]', 'red')
		sys.exit()                  
	elif opt in ("-f", "--file"): 
		outfile = arg

#############
# FUNCTIONS #
#############

##########
# SCRIPT #
##########

#Get the current date
now = datetime.datetime.now()
curr_date = str(now.year) + '.' + str("%02d" % (now.month,)) + '.' + str("%02d" % (now.day,))

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
sys.path.append('/Users/carloartieri/bin/python') #Set python path for common functions
import argparse		#Access to long command-line parsing	
import datetime		#Access to calendar/clock functions
import re			#Access to REGEX splitting
import math			#Access to math functions
import common		#My custom common python scripts

##########################
# COMMAND-LINE ARGUMENTS #
##########################

parser = argparse.ArgumentParser(description='Zip tables together.', add_help=False)
req = parser.add_argument_group('Required arguments:')
req.add_argument('-i','--infile', action="store", dest="infile", help='Input table', required=True, metavar='')
req.add_argument('-o','--outfile', action="store", dest="outfile", help='Zipped output table', required=True, metavar='')
#req.add_argument('-c','--cols', action="store", dest="colstep", help='1-based start column and step', nargs=2, required=True, metavar=('COL','STEP'))
opt = parser.add_argument_group('Optional arguments:')
#opt.add_argument('-s','--sep', action="store", dest="sep", help='Column seperator [default: \'\\t\']', default='\t', metavar='')
opt.add_argument("-h", "--help", action="help", help="show this help message and exit")
args = parser.parse_args()

#############
# FUNCTIONS #
#############

##########
# SCRIPT #
##########

infile = open(FILE, 'r')
for line in infile:

	line = line.rstrip('\n')
	line_t = line.split('\t')

"""

#Open up a file and write the default python script header
script = open(outfile, "w")
script.write(script_header)
script.close()

