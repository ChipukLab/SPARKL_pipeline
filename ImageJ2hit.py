#! usr/bin/python3

import argparse
import os
import subprocess
import sys

import IncuCyte2hit

def main(ijm, folder, c1, c2, roi, pair):
	os.system('cls' if os.name == 'nt' else 'clear')
	if ijm == None:
		ijm = input('Provide path to ImageJ/Fiji macro script:\n').strip()
	if folder == None:
		folder = input('Provide path to parent directory containing image files:\n').strip()
	if c1 == None:
		c1 = input('Provide substring for files containing first signal (e.g.: "green"):\n')	
	if c2 == None:
		c2 = input('Provide substring for files containing overlap signal (e.g.: "yellow"):\n')	
	if roi == None:
		roi = input('Provide path to file which will be used for ROI identification:\n').strip()

	arg = c1+','+c2+','+roi+','+folder
	subprocess.run(['/Applications/Fiji.app/Contents/MacOS/ImageJ-macosx', '--console', '-macro', ijm, arg])

	#folder = folder[folder.rfind('/') + 1:]
	if pair == True:
		green_file = os.path.dirname(folder) + '/results' + c1.upper() + '.csv'
		yellow_file = os.path.dirname(folder) + '/results' + c2.upper() + '.csv'
		output_file = os.path.dirname(folder) + '/output' + c1[0].upper() + c2[0].upper() + '.csv'
		IncuCyte2hit.main(green_file, yellow_file, output_file, ',', 'False')
	print('Done!')
		
if __name__ == '__main__':
	# Parse terminal command line and run program
	parser = argparse.ArgumentParser()
	parser.add_argument('--ijm', default=None, type=str)
	parser.add_argument('--folder', default=None, type=str)
	parser.add_argument('--c1', default=None, type=str)
	parser.add_argument('--c2', default=None, type=str)
	parser.add_argument('--roi', default=None, type=str)
	parser.add_argument('--pair', default=True, action='store_false')
	args = parser.parse_args(sys.argv[1:])
	main(args.ijm, args.folder, args.c1, args.c2, args.roi, args.pair)