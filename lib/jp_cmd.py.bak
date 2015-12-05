#!/usr/bin/env python

# $Header: //depot/icd_tools/bcm_tool/main/block/bcm_timing/calculate_cmd.py#4 $

__author__ = "Peter Wu (pwu@altera.com)"
__version__ = "$Revision: #4 $"
__date__ = "$Date: 2014/10/31 $"
__copyright__ = "Copyright 2014 Altera Corporation."

# System modules
import optparse
import os
import re
import random
import subprocess
import datetime
import sys

# Local modules
import jp_html
int_regex = re.compile(r"^\d+\.\s+", re.IGNORECASE)
def fix_box_string(txt):
	txt = int_regex.sub('', txt.strip())
	txt = txt[:1].upper() + txt[1:] if txt else ''
	return txt


class JpTopicBox:
	'''
	Represents the single question and answer box
	'''

	############################################################################
	def __init__(self):

		self._question = ""
		self._answer = ""
		self._points = 100

	################################################################################
	def set_answer(self, txt):
		self._answer = fix_box_string(txt)

	################################################################################
	def set_question(self, txt):
		self._question = fix_box_string(txt)

	################################################################################
	def get_question(self):
		return self._question

	################################################################################
	def get_answer(self):
		return self._answer

	################################################################################
	def get_points(self):
		return self._points

	################################################################################
	def dump(self):
		print '  question = %s' % self._question
		print '    answer = %s' % self._answer
		print '    points = %d' % self._points

class JpTopic:
	'''
	Represents the topic column
	'''

	############################################################################
	def __init__(self, topic):
		self._topic = topic.title()
		self._boxes = list()

	################################################################################
	def get_name(self):
		return self._topic

	################################################################################
	def sort_boxes(self, cached):
		'''
		Sort the boxes and assign values
		'''
		max_rows = 5
		ignored_boxes = list()
		keep_boxes = list()
		for box in self._boxes:
			if box.get_question() in cached:
				ignored_boxes.append(box)
			else:
				keep_boxes.append(box)

		# Shuffle the questions
		random.shuffle(keep_boxes)
		random.shuffle(ignored_boxes)

		# In case kept boxes have little left
		while len(keep_boxes) < max_rows and len(ignored_boxes) > 0:
			keep_boxes.append(ignored_boxes.pop(0))
			#print "Reusing: %s" % (keep_boxes[-1].get_question())

		self._boxes = sorted(keep_boxes[:max_rows], key=lambda box: box.get_points())
		value = 0
		for box in self._boxes:
			value += 100
			box._points = value
			cached[box.get_question()] = True

	################################################################################
	def get_boxes(self):
		'''
		return the boxes
		'''
		return self._boxes

	################################################################################
	def add_box(self, question, answer, points):
		'''
		Add a box
		'''
		box = JpTopicBox()
		box.set_question(question)
		box.set_answer(answer)
		if points:
			box._points = points

		self._boxes.append(box)

	################################################################################
	def dump(self):
		print 'topic = %s' % self._topic
		for box in self._boxes:
			box.dump()

class JpCmd:
	'''
	Generates Jeopardy game
	'''

	############################################################################
	def __init__(self):
		self._options = None
		self._limit = 1000
		self._used_question = dict()
		self._topics = list()
		self._db_files = list()
		random.seed()

	################################################################################
	def _count_topic(self, file_obj, fullpath):
		'''
		Count the number of questions
		'''
		question_start_regex = re.compile(r"^\s*<q>")
		question_end_regex = re.compile(r"^\s*</q>")
		is_question_regex = re.compile(r"^.+\?")
		points_regex = re.compile(r"^\s*points:(\d+)")
		non_empty_regex = re.compile(r"\S")

		last_question = ""
		toggle_is_question = True
		lineno = 1
		unused_count = 0
		used_count = 0
		in_q = False
		expect_answer = False

		for line in file_obj.readlines():
			lineno += 1
			m = points_regex.match(line)
			if m:
				pass
			elif question_start_regex.match(line):
				if expect_answer:
					print 'Internal Error: No answer found for this question: %s (line %d, file %s)' % (last_question, lineno, fullpath)
				in_q = True
				last_question = ''
			elif in_q:
				if question_end_regex.match(line):
					expect_answer = True
					in_q = False
					toggle_is_question = False
					if fix_box_string(last_question) in self._used_question:
						used_count += 1
					else:
						unused_count += 1
				else:
					last_question += '%s<br>' % line.strip()
			elif non_empty_regex.match(line):
				expect_answer = False
				# Toggle between Q and A
				if toggle_is_question:
					if fix_box_string(line) in self._used_question:
						used_count += 1
					else:
						unused_count += 1
					toggle_is_question = False
					last_question = line
				elif is_question_regex.match(line):
					print 'Internal Error: Answer expected but found a question: %s (line %d, file %s)' % (line, lineno, fullpath)
				else:
					toggle_is_question = True
			else:
				pass

		if not toggle_is_question:
			print 'Internal Error: File ended without an answer for the question: %s (line %d, file %s)' % (last_question, lineno, fullpath)

		elif unused_count+used_count < 5:
			print 'Internal Error: The file contains less than 5 questions: %s' % (fullpath)

		return (unused_count, used_count)

	################################################################################
	def _show_options(self, start_dir, index=0, indent=""):
		'''
		Ask users to pick topics
		'''
		for root, dirs, files in os.walk(start_dir):

			for dir in dirs:

				print '%s%s' % (indent, dir.title())
				index = self._show_options(os.path.join(root, dir), index, indent+"  ")

			for file in files:

				fileName, fileExtension = os.path.splitext(file)
				if root == start_dir and fileExtension == '.txt':
					index+=1
					fullpath = os.path.join(root, file)
					with open(fullpath, 'r') as f:
						first_line = f.readline().strip()
						(unused_count, used_count) = self._count_topic(f, fullpath)
						print '%s%d. %-30s (%d new, %d old)' % (indent, index, first_line.title(), unused_count, used_count)
					self._db_files.append(fullpath)

		return index

	################################################################################
	def _get_unique_output_file(self, odir):
		for i in range(100):
			fname = os.path.join(odir, 'trivia%d.html' % i)
			if not os.path.isfile(fname):
				return fname
		return 'trivia_overflow.html'

	################################################################################
	def _get_cache_fname(self):
		'''
		Get the cache
		'''
		now = datetime.datetime.now()
		return "../cache/mon%d_day%d.txt" % (now.month, now.day)

	################################################################################
	def _read_cache(self):
		'''
		Read the cache
		'''
		file = self._get_cache_fname()
		if os.path.isfile(file):
			with open(file, 'r') as f:
				for line in f.readlines():
					self._used_question[line.strip()] = True
				print 'Read: %s (%d keys)' % (file, len(self._used_question))

	################################################################################
	def _write_cache(self):
		'''
		Write the cache
		'''
		file = self._get_cache_fname()
		with open(file, 'a') as f:
			for key in self._used_question.keys():
				print >> f, key
			print 'Wrote: %s' % file

	################################################################################
	def _create_topic(self, file):
		'''
		Read the database file and create JpTopic
		'''
		question_start_regex = re.compile(r"^\s*<q>")
		question_end_regex = re.compile(r"^\s*</q>")
		points_regex = re.compile(r"^\s*points:(\d+)")
		non_empty_regex = re.compile(r"\S")
		with open(file, 'r') as f:

			first_line = f.readline().strip()
			points = 0
			topic = JpTopic(first_line)
			self._topics.append(topic)
			toggle_is_question = True
			question = ''
			in_q = False

			for line in f.readlines():
				m = points_regex.match(line)
				if m:
					points = int(m.group(1))
				elif question_start_regex.match(line):
					in_q = True
					question = ''
				elif in_q:
					if question_end_regex.match(line):
						in_q = False
						toggle_is_question = False
					else:
						question += '%s<br>' % line.strip()
				elif non_empty_regex.match(line):
					# Toggle between Q and A
					if toggle_is_question:
						toggle_is_question = False
						question = line
					else:
						topic.add_box(question, line, points)
						toggle_is_question = True

		#topic.dump()

	################################################################################
	def _get_user_input(self):
		'''
		Return a list of user specified topics.
		'''
		db_file_indices = list()

		print ''
		print 'Choose five topics from the following:\n'
		self._show_options('.')
		print ''
		# set up available ID's to choose from
		user_selections = dict()
		total_keys = len(self._db_files)
		for i in range(total_keys):
			user_selections[str(i+1)] = False

		# Ask user input
		max_columns = 5
		for i in range(max_columns):
			id = raw_input('Pick a number (from 1 to %d) for topic #%d: ' % (total_keys, i+1))
			while not user_selections.has_key(id):
				id = raw_input('--   Try again! Pick a number (from 1 to %d) for column %d: ' % (total_keys, i+1))

			# choosing identical files is okay.
			if user_selections[id]:
				print "--   Warning: You chose %s already. That means you'll see a duplicate column!" % id
			else:
				user_selections[id] = True

			# calculate index
			file_index = int(id)-1
			db_file_indices.append(file_index)

		return db_file_indices

	################################################################################
	def _read_database(self):
		'''
		Read the database of questions and construct objects.
		'''
		db_file_indices = self._get_user_input()
		chosen_files = [self._db_files[index] for index in db_file_indices]

		# choosing identical files is okay.
		# that means you'd get to have more questions to choose from.
		print "\nGenerating Jeopardy game for the following topics:"
		for file in chosen_files:
			with open(file, 'r') as f:
				first_line = f.readline()
				print '> %s' % (first_line),

		for file in chosen_files:
			self._create_topic(file)

		return True

	################################################################################
	def _write_output(self):
		'''
		Write final output.
		'''
		htm_obj = jp_html.JpHtml(self._topics)
		content = htm_obj.get_output_lines()
		ofile = self._get_unique_output_file('C:/Users/peterwu8/Desktop/Sunday School/Trivia')
		try:
			os.remove(ofile)
		except OSError:
			pass
		with open(ofile, 'w') as f:
			print >> f, content
			print 'Generated: %s' % ofile

		print subprocess.Popen(ofile, shell=True, stdout=subprocess.PIPE).stdout.read()
		return True

	################################################################################
	def _sort_topics(self):
		'''
		Sort the topics and set up numbers.
		'''
		self._topics = sorted(self._topics, key=lambda topic: topic.get_name())
		for topic in self._topics:
			topic.sort_boxes(self._used_question)		
		return True

	################################################################################
	def _execute_default(self):
		'''
		This function defines the default behavior.
		'''

		self._read_cache()

		if not self._read_database():
			return 1

		if not self._sort_topics():
			return 1

		if not self._write_output():
			return 1

		self._write_cache()

		return 0

	################################################################################
	def execute(self, argv):
		'''
		Main entry point function for the class.
		Return 0 if successful.
		Return 1 otherwise.
		'''

		# Output results
		return self._execute_default()
