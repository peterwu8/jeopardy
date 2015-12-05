#! /usr/bin/env python

################################################################################
#
# $Header: //depot/icd_tools/bcm_tool/main/block/bcm_timing_mode_tool.py#5 $
#
# Description:	Provides subcommands for BCM timing modes.
#
# Author:		Peter Wu
#
#				Copyright (c) Altera Corporation 2014
#				All rights reserved.
#
################################################################################

__author__ = "Peter Wu (pwu@altera.com)"
__version__ = "$Revision: #5 $"
__date__ = "$Date: 2014/10/03 $"
__copyright__ = "Copyright 2014 Altera Corporation."

#-----------------------------------------------------------
# System modules
#-----------------------------------------------------------
import re
import sys

#-----------------------------------------------------------
# Local modules
#-----------------------------------------------------------
import lib.jp_cmd as n_jp_cmd

############################################################################
def execute_help(argv):
	"""
	Prints help for subcommands.
	"""

	if len(argv) < 1:
		# Example: bcm_timing_mode_tool.py help
		print_default_help()
		return 0
	else:
		# Example: bcm_timing_mode_tool.py help calculate
		command = argv[0]
		return dispatch_command(command, list())


# This is a dict (hash) of every subcommand to an implementation
# method for that subcommand. Used to dispatch commands (see below).
COMMAND_MAP = {
	"jp": n_jp_cmd.JpCmd().execute,
	"help": execute_help,
}

############################################################################
def print_default_help():
	"""
	Prints default help.
	"""

	print ('''
	BCM timing mode tool

	Usage:

	  %(prog)s [sub-command] [options]

	Try one of the sub-commands:

	  %(prog)s jp [options]         Option to generate jp game.
	  %(prog)s help [sub-command]   Option to display help for the sub-command
	  %(prog)s help                 Option to display this top-level help
	''' % { "prog":"python game.py" })

############################################################################
def dispatch_command(command, argv):
	"""
	Dispatches the appropriate sub-command based on command line
	arguments.
	"""

	if command in COMMAND_MAP:
		return COMMAND_MAP[command](argv)
	else:
		n_putil.print_error("Unknown sub-command '%s'" % (command))
		print_default_help()
		return 1

################################################################################
# Description:	Main function.
# Arguments:	defined by getopt
################################################################################
def altera_main(argv):
	"""
	Entry point function.
	"""
	if len(argv) <= 1:
		print_default_help()
		return 0

	command = argv[1]

	# Now call dispatcher for command and the rest of the options + args
	return dispatch_command(command, argv[2:])

#############
#	Main	#
#############

# The main function. Only when this script is executed is __main__
# called. Otherwise, this .py script can be imported and methods
# invoked for test purposes.

if "__main__" == __name__:

	try:

		return_code = altera_main(sys.argv)

##	except Exception, e:
##		print "Error: %s" % str(e)
##		return_code = 1
	except KeyboardInterrupt:
		print ("\n")
		print ("Good bye!")
		sys.exit(1)

	sys.exit(return_code)
