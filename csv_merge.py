# script to merge the multiple csv data into single csv
import os
import csv
import json
from datetime import datetime, date, timedelta

def merge_csvs(filelist, out_fname):
	length = 0
	with open(out_fname, "a") as out:
		# write first file
		lines = read_file(filelist[0], include_header=True)
		if lines: out.writelines(lines)

		lines = []

		for fname in filelist[1:]:
			lines = read_file(fname)
			if lines: out.writelines(lines)

def read_file(fname, include_header=False):
	# read file and return lines
	lines = []
	with open(fname, "r") as file:
		lines = file.readlines()

	lines = lines if include_header else lines[1:]
	return lines

def get_date(_min, _max):
	# generate date
	date = None
	max_date = None
	
	date = datetime.now() if not _min else datetime.strptime(_min, "%Y-%m-%d")
	max_date = datetime.now() if not _max else datetime.strptime(_max, "%Y-%m-%d")

	while date <= max_date:
		yield date.strftime("%Y-%m-%d")
		date = date + timedelta(days=1)

def get_file_list(base_dir, from_date, to_date, include_files):
	# Get the list of files
	filelist = { fname: [] for fname in include_files }

	def is_valid(file, base_dir, date):
		# check if valid file
		is_file = os.path.isfile(os.path.join(dir_path, file))
		is_csv = True if all([file.endswith("csv"), is_file]) else False

		check_fnames = ["{0}{1}".format(fname,date) for fname in include_files]
		is_included_file = True if all([is_file, is_csv, [fname for fname in check_fnames if fname in file]]) else False

		if all([is_file, is_csv, is_included_file]):
			return True
		else:
			return False

	def append_to_filelist(base_dir, files, date):
		# append to file list
		for key in filelist.keys():
			fname = "{0}{1}".format(key, date)
			if fname in file:
				_temp = filelist.get(key, [])
				_temp.append(os.path.join(dir_path, file))

	if not all([base_dir, from_date, to_date, include_files]):
		raise Exception("Invalid arguments")
	
	if not os.path.isdir(base_dir):
		raise Exception("Report Path does not exists")

	for date in get_date(from_date, to_date):
		if not os.path.isdir(base_dir):
			continue

		dir_path = "{base_dir}/{date}".format(base_dir=base_dir, date=date)
		if not os.path.exists(dir_path):
			continue

		for file in os.listdir(dir_path)[:]:
			if is_valid(file, dir_path, date):
				append_to_filelist(base_dir, file, date)


	return filelist

if __name__ == "__main__":
	config = {}
	with open("./merge_file_config.json", "r") as file:
		config = json.loads(file.read())
	
	if not config:
		print "config not found"
	else:
		to_date = config.get("to_date")
		from_date = config.get("from_date")
		base_dir = config.get("base_dir")
		out_fname = config.get("out_fname")
		include_files = config.get("include_files")

		filelist = get_file_list(base_dir, from_date, to_date, include_files)

		for fname, files in filelist.iteritems():
			fname = "{out_fname}/{fname}{from_date}-{to_date}.csv".format(
					out_fname=out_fname,
					fname=fname,
					from_date=from_date,
					to_date=to_date
				)

			merge_csvs(files, fname)