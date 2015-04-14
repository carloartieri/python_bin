#!/usr/bin/python

# Created on: 2015.04.13 
# Author: Carlo Artieri

##############################
# HISTORY AND THINGS TO FIX  #
##############################
#2015.04.13 - Initial script

###########
# MODULES #
###########
import sys			#Access to simple command-line arguments
sys.path.append('/Users/carloartieri/bin/python') #Set python path for common functions
import argparse		#Access to long command-line parsing	
import datetime		#Access to calendar/clock functions
import re			#Access to REGEX splitting
import math			#Access to math functions
import subprocess	#Access to shell commands
import random		#Access to random number generator
#import common		#My custom common python scripts

##########################
# COMMAND-LINE ARGUMENTS #
##########################

parser = argparse.ArgumentParser(description='Zip tables together.', add_help=False)
req = parser.add_argument_group('Required arguments:')
req.add_argument('-f','--fasta', action='store', dest='fasta', help='Input fasta file', required=True, metavar='')
req.add_argument('-l','--length', action='store', dest='length', type=int, help='Length of sequences to determine mappability', required=True, metavar='')

req.add_argument('-o','--outfile', action='store', dest='outfile', help='Zipped output table', required=True, metavar='')
#req.add_argument('-c','--cols', action='store', dest='colstep', help='1-based start column and step', nargs=2, required=True, metavar=('COL','STEP'))
opt = parser.add_argument_group('Optional arguments:')
#opt.add_argument('-s','--sep', action='store', dest='sep', help='Column seperator [default: '\t']', default='\t', metavar='')
opt.add_argument('-h', '--help', action='help', help='show this help message and exit')
args = parser.parse_args()

#############
# FUNCTIONS #
#############

def fasta_to_dict(file):

	fasta_file = open(file, "r")	#Open the file for reading
	fasta_dic = {}
	
	for line in fasta_file:
		line = line.rstrip('\n')
		if re.match('^>', line):
			line_split = line.split(' ')	#By default keeps only first word of the header.
			header = line_split[0].translate(None, '>')
			fasta_dic[header] = ''
		else:
			fasta_dic[header] += line	
	
	fasta_file.close()
	
	return fasta_dic

##########
# SCRIPT #
##########

#First step is to read in the FASTA sequence and create the 'dummy' FASTQ
fasta_dict = fasta_to_dict(args.fasta)

out_fastq = open(args.fasta + '.temp.fastq', 'w')	#Open a temporary file where we'll hold
													#our dummy FASTQ
keys = sorted(fasta_dict.keys())
for key in keys:
	seq_len = len(fasta_dict[key])

	#Tile across the sequence with substrings
	for i in range(seq_len):
		stop = i + args.length #Set the substr
		if stop <= seq_len:
			subseq = fasta_dict[key][i:stop]
			qual = '~' * args.length #Quality will be max value
			out_fastq.write(str(key)+'|'+str(i)+'|'+str(stop)+'\n'+subseq+'\n'+'+\n'+qual+'\n')
out_fastq.close()

#Now we map the FASTQ back to the genome




#infile = open(FILE, 'r')
#for line in infile:

#	line = line.rstrip('\n')
#	line_t = line.split('\t')

