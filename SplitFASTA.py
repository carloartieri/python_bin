#!/usr/bin/python

# Created on: 2015.04.28 
# Author: Carlo Artieri

##############################
# HISTORY AND THINGS TO FIX  #
##############################
#2015.04.28 - Initial script

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

parser = argparse.ArgumentParser(description='This script breaks a multi-sequence FASTA file into multiple FASTA files, each containing one sequence. The corresponding filenames are the headers of each sequence, up to the first space + \'.fasta\'', add_help=False)
req = parser.add_argument_group('Required arguments:')
req.add_argument('-i','--infile', action='store', dest='infile', help='Input FASTA file', required=True, metavar='')
req.add_argument('-o','--outloc', action='store', dest='outloc', help='Location for split FASTA files (creates if nonexistent)', required=True, metavar='')
opt = parser.add_argument_group('Optional arguments:')
opt.add_argument('-h', '--help', action='help', help='show this help message and exit')
args = parser.parse_args()

#############
# FUNCTIONS #
#############

##########
# SCRIPT #
##########
#Strip trailing slash on directory
args.outloc = args.outloc.rstrip('/')

#Check if outdir exists, if not, create
if os.path.isdir(args.outloc) is False:
	os.makedirs(args.outloc)

first = 1
infasta = open(args.infile, 'r')
for line in infasta:
	line = line.rstrip('\n')
	line_t = line.split('\t')

	#Check for header
	if re.match('^>', line) and first == 1:
		line_split = line.split(' ')
		header = line_split[0].translate(None, '>')
		outfile = open(str(args.outloc) + '/' + str(header) + '.fasta', 'w')
		outfile.write('>' + str(line) + '\n')
		first = 0
	elif re.match('^>', line) and first == 0:
		outfile.close()
		line_split = line.split(' ')
		header = line_split[0].translate(None, '>')
		outfile = open(str(args.outloc) + '/' + str(header) + '.fasta', 'w')
		outfile.write('>' + str(line) + '\n')
		first = 0
	else:
		outfile.write(str(line) + '\n')
infasta.close()
outfile.close()