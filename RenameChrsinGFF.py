#!/usr/bin/python

# Created on: 2015.04.24 
# Author: Carlo Artieri

##############################
# HISTORY AND THINGS TO FIX  #
##############################
#2015.04.24 - Initial script

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
import random		#Access to random number generator

##########################
# COMMAND-LINE ARGUMENTS #
##########################

epilog = """\
This script renames the chromosomes (first column) of GFF/GTF annotation files based on a user-
supplied correspondence table.

If the GFF/GTF chromosome is not found in the correspondence table, a warning is printed and
the chromosome is ommitted from the output. 

More detailed description of options follows:

-t/--table
	A tab-delimited table with two columns, where column one contains the original chromosome
	name, and column two contains the new chromosome name.
	
"""
class CustomFormatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter):
    pass

parser = argparse.ArgumentParser(description='Rename the chromosomes in a GFF/GTF file based on user-specified conversion table', add_help=False, epilog=epilog, formatter_class=CustomFormatter)
req = parser.add_argument_group('Required arguments:')
req.add_argument('-t','--table', action='store', dest='table', help='Chromosome conversion table', required=True, metavar='')
req.add_argument('-i','--infile', action='store', dest='infile', help='Input GFF/GTF', required=True, metavar='')
req.add_argument('-o','--outfile', action='store', dest='outfile', help='Output GFF/GTF', required=True, metavar='')
opt = parser.add_argument_group('Optional arguments:')
opt.add_argument('-h', '--help', action='help', help='show this help message and exit')
args = parser.parse_args()

#############
# FUNCTIONS #
#############

##########
# SCRIPT #
##########

#Read in the conversion table as a dictionary
conv_dict = {}
table = open(args.table, 'r')
for line in table:
	line = line.rstrip('\n')
	line_t = line.split('\t')
	conv_dict[line_t[0]] = line_t[1]
table.close()

out_file = open(args.outfile, 'w')
in_file = open(args.infile, 'r')
for line in in_file:
	if re.match('^#', line):
		out_file.write(line)
		continue
	line = line.rstrip('\n')
	line_t = line.split('\t')

	if line_t[0] in conv_dict:
		line_t[0] = conv_dict[line_t[0]]		
		outline = '\t'.join(line_t)
		out_file.write(str(outline) + '\n')
	else:
		print str(line_t[0]) + ' NOT IN CONVERSION TABLE!!!'
in_file.close()
out_file.close()