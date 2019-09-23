#! usr/bin/python3

# Script for 2-hit single-cell analyses using IncuCyte images processed through ImageJ.
# Takes csv data from signal and overlap masks, sorts, pairs, and provides data for graphing.

# USAGE (from Terminal):
# "$ python3 IncuCyte2hit.py [optional flags]"
# 	flags:
# 	-h or --help:
# 		provides help text for script usage
# 	--signal_file:
# 		csv file containing data for first signal;
# 		if script is in the same directory as file, use name of file; else, provide path;
# 		if not provided or incorrect usage, user will be prompted during execution
# 	--overlap_file:
# 		csv file containing data for overlap signal;
# 		if script is in the same directory as file, use name of file; else, provide path;
# 		if not provided or incorrect usage, user will be prompted during execution
# 	--output_file:
# 		destination file to write the output csv file for graphing;
# 		if not provided, prints "output.csv" to directory containing signal_file;
# 		if name, prints "{name}" to same directory; if path, prints "output.csv" to path 
# 	--delimiter:
# 		character used to separate data columns in csv file; defaults to ","
# 	--verbose:
# 		if used, script will print tables from intermediate steps to terminal window	

import argparse
import csv
import os
import sys

def main(green_file, yellow_file, output_file, delimiter, verbose):
	# Manipulate CSV file data and output data for graphing
	# Get location of files if not included in command line
	os.system('cls' if os.name == 'nt' else 'clear')
	green_file = getFilePath(green_file, 'signal')
	yellow_file = getFilePath(yellow_file, 'overlap')
	if output_file == None:
		# No flag is provided: "output.csv" printed in same directory as input file
		output_file = os.path.dirname(os.path.abspath(green_file)) + '/output.csv'
	elif os.path.isdir(output_file) == False and '.' in output_file and '/' in output_file:
		# Input resembles a directory path with desired file name
		output_file = output_file[output_file.rfind('/'):]
		print('Output directory not found.')
		print('Printing "'+ output_file[1:] +'" to same directory as input files:')
		output_file = os.path.dirname(os.path.abspath(green_file)) + output_file
	elif '.' in output_file and '/' not in output_file:
		# Input is assumed to be desired filename and not path
		output_file = os.path.dirname(os.path.abspath(green_file)) + '/' + output_file
	elif os.path.isdir(output_file) == True:
		# Input is valid directory
		print('Printing "output.csv" to output directory:')
		output_file = os.path.dirname(os.path.abspath(green_file)) + '/output.csv'
	else:
		# Input resembles a directory path but is broken
		print('Output directory not found.')
		print('Printing "output.csv" to same directory as input files:')
		output_file = os.path.dirname(os.path.abspath(green_file)) + '/output.csv'
	print('output file path:\n', output_file)

	# Unpack, sort, and identify hits for green data
	green_list, fieldnames = csvRead(green_file, 'Green', delimiter)
	green_list_sorted = sortTuples(green_list, fieldnames, 'X', 'Slice')
	green_hit_list = hitList(green_list_sorted, fieldnames)
	# Unpack, sort, and identify hits for yellow data
	yellow_list, fieldnames = csvRead(yellow_file, 'Yellow', delimiter)
	yellow_list_sorted = sortTuples(yellow_list, fieldnames, 'X', 'Slice')
	yellow_hit_list = hitList(yellow_list_sorted, fieldnames)
	# Take sorted lists and returns list with both slice values per line
	greenyellow_list, fieldnames = mergeLists(green_hit_list, yellow_hit_list, fieldnames)
	# Sort list by first signal and print, or convert to csv and export to output file
	greenyellow_list_sorted = sortTuples(greenyellow_list, fieldnames, 't1', 't2')
	if verbose == True:
		# Print each intermediate data table if "verbose" flag is used
		print('\n\n\n')
		pprint(green_list_sorted, 'First Signal Data Sorted By ROI')
		pprint(yellow_list_sorted, 'Second Signal Data Sorted By ROI')
		pprint(green_hit_list, 'First Signal Hit Table')
		pprint(yellow_hit_list, 'First Signal Hit Table')
		pprint(greenyellow_list, 'Time To Signal')
	print('.\n.\n.\n"' + output_file[output_file.rfind('/') + 1:] + '" printed to ' + os.path.dirname(output_file))	
	csvWrite(greenyellow_list_sorted, output_file, delimiter)
	

def getFilePath(file, data):
	# Prompt for file path if not given as flags in command line
	if file == None:
		file = input('Provide path or name of file containing '+data+' data: ')
	while os.path.isfile(file) == False:
		if file[-1] == ' ':	
			file = file[:-1]
		else:	
			print('"'+file+'" is not a valid file in this folder')
			file = input('Provide path or name of file containing '+data+' data: ')
	print(data, 'data path:\n', os.path.abspath(file))
	return file			


def csvRead(csv_file, channel_name, delimiter):
	# Convert a CSV file to a list of tuples
	# Tuples are useful for saying "These data belong to the same item in list"
	with open(csv_file) as file:
		content = list(csv.reader(file, delimiter=delimiter))
		fieldnames = content[0]
		fieldnames[0] = channel_name
		for row in content[1:]:
			for i in range(len(row)):
				row[i] = float(row[i])
		return content, fieldnames

def sortTuples(the_list, fieldnames, primary, secondary):
	# Sort a list of tuples by specified keys ("columns") and return ordered list
	primary, secondary = fieldnames.index(primary), fieldnames.index(secondary)
	the_list[1:] = sorted(the_list[1:], key=lambda x: (float(x[primary]), float(x[secondary])))
	return the_list


def hitList(the_list, fieldnames):
	# Identify slice with first instance of a Mean > 0 and return list of tuples
	# This is equivalent to saying "timepoint at which ROI#n labeled"
	X, Mean = fieldnames.index('X'), fieldnames.index('Mean')
	hit_list = [fieldnames]
	previous_x = 0
	for row in the_list[1:]:
		current_x = row[X]
		if current_x != previous_x and row[Mean] != 0:
			hit_list.append(row)
			previous_x = current_x
	return hit_list


def mergeLists(list1, list2, fieldnames):
	# Returns list of slices for matched X values; also a list for slice differences
	# Equvalent to saying "For each ROI, when was the first and second labeling event"
	X, Slice = fieldnames.index('X'), fieldnames.index('Slice')
	fieldnames = ['ID#', 't1', 't2', '\u0394t']
	new_row, merged_list = [], [fieldnames]
	for row in list1[1:]:
		row_index = list1.index(row)
		if row[X] != list2[row_index][X]:
			print("ERROR")
		new_row = [row_index, row[Slice], list2[row_index][Slice], list2[row_index][Slice] - row[Slice]]
		merged_list.append(new_row)	
	return merged_list, fieldnames


def csvWrite(the_list, output_file, delimiter):
	# Takes user list and writes to a CSV file for use in graphing software
	if output_file == None:
		pprint(the_list)
	else:
		with open(output_file, 'w') as output:
			writer = csv.writer(output, delimiter=delimiter)
			writer.writerows(the_list)
		output.close()


def pprint(the_list, table_title):
	# "Pretty prints" tables in a reader-friendly format for QA purposes
	# Prints first row which contains fieldnames ("headers")
	if len(the_list[0]) == 4:
		print('{:-^16}'.format(table_title))
		print(' {:>3}  {:^2}  {:^2}  {:^2}'.format(*the_list[0]))
		for row in the_list[1:]:
			print(' {:>3n}  {:>2n}  {:>2n}  {:>2n}'.format(*row))
	if len(the_list[0]) == 6:
		print('{:-^46}'.format(table_title))
		print('{:>6}  {:^3}  {:^7} {:^7}  {:^7}  {:^2}'.format(*the_list[0]))
		for row in the_list[1:]:
			print(' {:>5n}  {:>3n}  {:>7n}  {:>7n}  {:>7n}  {:>2n}'.format(*row))
	print('\n\n\n')


if __name__ == '__main__':
	# Run main function and parse arguments from command line
	parser = argparse.ArgumentParser(description=\
		'Script to pair and order two-hit IncuCyte data analyzed through ImageJ')
	# Mandatory args
	# Optional args
	parser.add_argument('--signal_file', default=None, type=str, help=\
		'Path (or name if in same directory) of file containing data for signal events')
	parser.add_argument('--overlap_file', default=None, type=str, help=\
		'Path (or name if in same directory) of file containing data for overlap events')
	parser.add_argument('--output_file', default=None, type=str, help=\
		'Path for where to write output file, or name and write to same directory')
	parser.add_argument('--delimiter', default=',', type=str, help=\
		'Character used to separate values in data files; also used in output file')
	parser.add_argument('--verbose', default=False, action='store_true',help=\
		'If used, terminal window will print intermediate data tables')
	# Parse and run
	args = parser.parse_args(sys.argv[1:])
	main(args.signal_file, args.overlap_file, args.output_file, args.delimiter, args.verbose)
