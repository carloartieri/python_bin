#!/usr/bin/python

# Created on: 2015.04.02 
# Author: Carlo Artieri

##############################
# HISTORY AND THINGS TO FIX  #
##############################
#2015.04.02 - Initial script
#			- Finished script and tested

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

parser = argparse.ArgumentParser(description='Concatenate tables based on a column of shared strings', add_help=False)
req = parser.add_argument_group('Required arguments:')
req.add_argument('-i','--infiles', action="store", dest="infiles", help='Comma-sep list of tables', required=True, metavar='')
req.add_argument('-o','--outfile', action="store", dest="outfile", help='Concatenated output table', required=True, metavar='')
#req.add_argument('-c','--cols', action="store", dest="colstep", help='1-based start column and step', nargs=2, required=True, metavar=('COL','STEP'))
opt = parser.add_argument_group('Optional arguments:')
opt.add_argument('-c','--col', action="store", dest="col", type=int, help='1-based column for concatenation [default: 1]', default=1, metavar='')
opt.add_argument('-l','--limit', action="store", dest="lim", help='Comma-sep list: use only these columns [default: all]', default='all', metavar='')
opt.add_argument('-s','--sep', action="store", dest="sep", help='Column seperator [default: tab]', default='\t', metavar='')
opt.add_argument("-h", "--help", action="help", help="show this help message and exit")
args = parser.parse_args()

#############
# FUNCTIONS #
#############

##########
# SCRIPT #
##########
out_dict = {}	#This holds the concatenated output
args.col -= 1
table_list = args.infiles.split(',')	#List of tables
col_list = args.lim.split(',')
col_dict = {}
for i in col_list:
	col_dict[i] = 1 	#Dict stores columns to concatenate

#Concatenate the tables
for table in table_list:
	infile = open(table, 'r')
	for line in infile:
		line = line.rstrip('\n')
		line_t = line.split(args.sep)
		outline = []
		for i in range(len(line_t)):
			if i != args.col:
				if args.lim != 'all':
					if i in col_dict:
						outline.append(line_t[i])
				else:
					outline.append(line_t[i])
		outline = args.sep.join(outline)
		if str(line_t[args.col]) in out_dict:
			out_dict[line_t[args.col]] = out_dict[line_t[args.col]] + args.sep + outline
		else:
			out_dict[line_t[args.col]] = outline
	infile.close()

outfile = open(args.outfile, 'w')
#Print the output
keys = sorted(out_dict.keys())
for key in keys:
	outfile.write(str(key) + args.sep + out_dict[key] + '\n')
outfile.close()

