#!/usr/bin/python

# Created on: 2015.04.13 
# Author: Carlo Artieri

##############################
# HISTORY AND THINGS TO FIX  #
##############################
#2015.04.13 - Initial script
#			- Modified method I was previously using to extract sequences so that this is much 
#			  more efficient with large mammalian genomes.
#			- Tested on GFF and works
#2015.04.13	- Bug causing first exon skipping, fixed.
#2015.04.15 - Added in command to skip empty lines in GFF

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
epilog = """\
This script takes an annotation file in GFF or GTF format as well as a genomic sequence in 
FASTA format, and produces a new fasta file containining the the spliced (if appropriate) 
annotation features. The user should specify the annotation feature (default: exon) and 
identifier (default: gene) to pull out of large GFF/GTFs. Two points of interest:

1. The script recognizes GFF/GTFs based on their info column (column 9) and expects the following 
format: 

GFF: identifier=feature;
GTF: identifier "feature";

4. An error will be printed identifying each feature line that doesn't contain the specified
identifier.
	
"""
class CustomFormatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter):
    pass

parser = argparse.ArgumentParser(description='Produce a FASTA file of annotations contained within a GFF/GTF.', add_help=False, epilog=epilog, formatter_class=CustomFormatter)
req = parser.add_argument_group('Required arguments:')
req.add_argument('-g','--gff', action='store', dest='gff', help='Annotation file', required=True, metavar='')
req.add_argument('-f','--fasta', action='store', dest='fasta', help='Genome file in FASTA format', required=True, metavar='')
req.add_argument('-o','--outfile', action='store', dest='outfile', help='Output file in FASTA format', required=True, metavar='')
opt = parser.add_argument_group('Optional arguments:')
opt.add_argument('-e','--feature', action='store', dest='feature', help='The annotation feature of interest', default='exon', metavar='')
opt.add_argument('-i','--identifier', action='store', dest='id', help='The column 8 identifier of interest', default='gene', metavar='')
opt.add_argument('-r','--rev', action='store_true', dest='rev', help='Reverse-transcribe annotations on the negative strand?')
opt.add_argument('-v','--verbose', action='store_true', dest='ver', help='Print out current chromosome progress in 100 kb increments.')
opt.add_argument('-h', '--help', action='help', help='show this help message and exit')
args = parser.parse_args()

#############
# FUNCTIONS #
#############

def ReverseComplement(seq):
    # too lazy to construct the dictionary manually, use a dict comprehension
    seq1 = 'ATCGNTAGCNatcgntagcn'
    seq_dict = { seq1[i]:seq1[i+5] for i in range(20) if i < 5 or 10<=i<15 }
    return "".join([seq_dict[base] for base in reversed(seq)])

##########
# SCRIPT #
##########

#Generate dictionaries of starts and ends for each of the features of interest.
start_dict = {}
stop_dict = {}
or_dict = {}

gff = open(args.gff, 'r')
line_count = 1
for line in gff:
	#Skip commented lines and empty lines
	if re.match('^#', line):
		continue
	if not line.strip():
		continue

	line = line.rstrip('\n')
	line_t = line.split('\t')
	
	#Check if appropriate feature of interest.
	if line_t[2] != args.feature:
		continue

	#Test if the file is a GFF or GTF
	args.id = args.id.strip()
	gff_type = args.id + '='
	gtf_type = args.id + ' "'

	if gff_type in line_t[8]:
		line_t8_split = line_t[8].split(';')
		for i in line_t8_split:
			if gff_type in i:
				type_split = i.split('=')
				start = int(line_t[3])-1
				stop = int(line_t[4])-1
				or_dict[type_split[1]] = line_t[6]
				if line_t[0] in start_dict:
					if start in start_dict[line_t[0]]:
						start_dict[line_t[0]][start].append(type_split[1])
					else:
						start_dict[line_t[0]][start] = []
						start_dict[line_t[0]][start].append(type_split[1])
				else:
					start_dict[line_t[0]] = {}
					start_dict[line_t[0]][start] = []
					start_dict[line_t[0]][start].append(type_split[1])

				if line_t[0] in stop_dict:
					if stop in stop_dict[line_t[0]]:
						stop_dict[line_t[0]][stop].append(type_split[1])
					else:
						stop_dict[line_t[0]][stop] = []
						stop_dict[line_t[0]][stop].append(type_split[1])
				else:
					stop_dict[line_t[0]] = {}
					stop_dict[line_t[0]][stop] = []
					stop_dict[line_t[0]][stop].append(type_split[1])

	elif gtf_type in line_t[8]:
		line_t8_split = line_t[8].split(';')
		for i in line_t8_split:
			if gtf_type in i:
				type_split = i.split('"')
				start = int(line_t[3])-1
				stop = int(line_t[4])-1
				or_dict[type_split[1]] = line_t[6]
				if line_t[0] in start_dict:
					if start in start_dict[line_t[0]]:
						start_dict[line_t[0]][start].append(type_split[1])
					else:
						start_dict[line_t[0]][start] = []
						start_dict[line_t[0]][start].append(type_split[1])
				else:
					start_dict[line_t[0]] = {}
					start_dict[line_t[0]][start] = []
					start_dict[line_t[0]][start].append(type_split[1])

				if line_t[0] in stop_dict:
					if stop in stop_dict[line_t[0]]:
						stop_dict[line_t[0]][stop].append(type_split[1])
					else:
						stop_dict[line_t[0]][stop] = []
						stop_dict[line_t[0]][stop].append(type_split[1])
				else:
					stop_dict[line_t[0]] = {}
					stop_dict[line_t[0]][stop] = []
					stop_dict[line_t[0]][stop].append(type_split[1])
	else:
		print str(args.gff) + ' ' + str(line_count) + ' missing identifier ' + str(args.id)

	line_count += 1 
gff.close()

#Now go through the genome one nucleotide at a time and create a FASTA dict.
out_fasta_dict = {}	#This will store the output FASTA file before writing.

genome = open(args.fasta, 'r')
line_count = 1
curr_chr = ''
for line in genome:
	line = line.rstrip('\n')
	if re.match('^>', line):
		line_split = line.split(' ')	#By default keeps only first word of the header.
		curr_chr = line_split[0].translate(None, '>')
		nuc_count = 0 
		started_features = []
	else:
		#Here's where we have to go through nucs one-by-one.
		if curr_chr in start_dict:
			for i in line:
				if nuc_count in start_dict[curr_chr]:
					 for j in start_dict[curr_chr][nuc_count]:
					 	started_features.append(j)

				if not started_features:
					pass
				else:
					for feat in started_features:
						if feat in out_fasta_dict:
							out_fasta_dict[feat] = out_fasta_dict[feat] + i
						else:
							out_fasta_dict[feat] = i

				if nuc_count in stop_dict[curr_chr]:
					for j in stop_dict[curr_chr][nuc_count]:
					 	started_features.remove(j)
				nuc_count += 1
				if nuc_count % 1000000 == 0 and args.ver is True:
					print str(curr_chr) + ' ' + str(nuc_count) + ' bp done.'
genome.close()

#Now output the appropriate FASTA file.
out_fasta = open(args.outfile, 'w')
keys = sorted(out_fasta_dict.keys())
for key in keys:
	if or_dict[key] == '-' and args.rev is True:
		out_fasta_dict[key] = ReverseComplement(out_fasta_dict[key])

	out_fasta.write('>' + key + '\n' + out_fasta_dict[key] + '\n')
out_fasta.close()






	

