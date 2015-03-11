#!/usr/bin/python

# Created on: 2015.03.06 
# Author: Carlo Artieri

##############################
# HISTORY AND THINGS TO FIX  #
##############################
#2015.03.06 - Initial script
#	- Add in don't test for header flag
#
#2015.03.07
#	- Added header flag and suffix for zipped columns.
#	- Modify header to test for line 1, make sure script deals with alpha columns (NAs),
#	  
#2015.03.07
#	- Added option to take average of columns.

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

parser = argparse.ArgumentParser(description="Sum specific columns in a table producing a new table replacing these columns with their sums." + common.ansi_colors['red'], add_help=False, formatter_class=argparse.RawTextHelpFormatter)
req = parser.add_argument_group("Required arguments:")
req.add_argument("-i","--infile", action="store", dest="infile", help="Input table", required=True, metavar="FILE", type=str)
req.add_argument("-o","--outfile", action="store", dest="outfile", help="Zipped output table", required=True, metavar="FILE", type=str)
req.add_argument("-c","--cols", action="store", dest="colstep", help="1-based start, zip offset, and step", nargs=3, required=True, metavar=("START","OFF","STEP"), type=int)
opt = parser.add_argument_group("Optional arguments:")
opt.add_argument("-m","--mode", action="store", dest="mode", help="mode [def: sum], average", default="sum", choices=['sum', 'average'], metavar="")
opt.add_argument("-s","--suff", action="store", dest="suff", help="Suffix to add to header", metavar="")
opt.add_argument("-p","--parse", action="store", dest="parse", help="Column separator [default: \"\\t\"]", default="\t", metavar="")
opt.add_argument("-x", "--ignoreheader", dest="ignore", action="store_true", help="Do not zip header")
opt.add_argument("-h", "--help", action="help", help="show this help message and exit\n" + common.ansi_colors['reset'])
args = parser.parse_args()

#############
# FUNCTIONS #
#############

#From: http://stackoverflow.com/questions/18715688/find-common-substring-between-two-strings
def common_start(sa, sb):
    def _iter():
        for a, b in zip(sa, sb):
            if a == b:
                yield a
            else:
                return

    return ''.join(_iter())

##########
# SCRIPT #
##########

#Convert start column to zero-based
args.colstep[0] -= 1

outfile = open(args.outfile, "w")

infile = open(args.infile, "r")
count = 0	#Line count to test header
for line in infile:

	zip_line = []	#This will store the zipped results
	zip_1 = args.colstep[0]
	zip_2 = None

	line = line.rstrip('\n')
	line_t = line.split(args.parse)
	
	#Test if the line is a header or contains text
	if count == 0:
		if args.ignore is False:
			i = 0
			while i < len(line_t):
				if i < args.colstep[0]:
					zip_line.append(line_t[i])
				
				elif i == zip_1:
					zip_2 = zip_1 + args.colstep[1]
					#Find the common start in the headers
					zip_line.append(common_start(line_t[zip_1], line_t[zip_2]) + args.suff)
					
					zip_1 += args.colstep[2]
					
				elif i != zip_1 and i != zip_2:
					zip_line.append(line_t[i])	 
					
				i += 1
			
			outfile.write(args.parse.join(zip_line) + '\n')
			
		else:
			outfile.write(str(line) + '\n')

	else:
		i = 0
		while i < len(line_t):
			if i < args.colstep[0]:
				zip_line.append(line_t[i])
			
			elif i == zip_1:
				zip_2 = zip_1 + args.colstep[1]
				#Sum the lines
				
				#Test for alpha - if so, zipped columns are 'NA'
				#if re.match('[a-zA-Z_]',line_t[1]):
				
				if args.mode == 'sum':
					zip_line.append(str(float(line_t[zip_1]) + float(line_t[zip_2])))
				elif args.mode == 'average':
					zip_line.append(str((float(line_t[zip_1]) + float(line_t[zip_2]))/2))
				zip_1 += args.colstep[2]
				
			elif i != zip_1 and i != zip_2:
				zip_line.append(str(line_t[i]))	 
				
			i += 1
		
		outfile.write(args.parse.join(zip_line) + '\n')
	count += 1

infile.close()		
outfile.close()