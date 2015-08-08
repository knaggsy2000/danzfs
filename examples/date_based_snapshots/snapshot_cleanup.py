#!/usr/bin/env python
# -*- coding: utf-8 -*-

#########################################################################
# Copyright/License Notice (BSD License)                                #
#########################################################################
#########################################################################
# Copyright (c) 2012-2013, Daniel Knaggs                                #
# All rights reserved.                                                  #
#                                                                       #
# Redistribution and use in source and binary forms, with or without    #
# modification, are permitted provided that the following conditions    #
# are met: -                                                            #
#                                                                       #
#   * Redistributions of source code must retain the above copyright    #
#     notice, this list of conditions and the following disclaimer.     #
#                                                                       #
#   * Redistributions in binary form must reproduce the above copyright #
#     notice, this list of conditions and the following disclaimer in   #
#     the documentation and/or other materials provided with the        #
#     distribution.                                                     #
#                                                                       #
#   * Neither the name of the author nor the names of its contributors  #
#     may be used to endorse or promote products derived from this      #
#     software without specific prior written permission.               #
#                                                                       #
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS   #
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT     #
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR #
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT  #
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, #
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT      #
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, #
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY #
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT   #
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE #
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.  #
#########################################################################

from danzfs import *
from datetime import *

import subprocess


# Variables
COLOUR_LOGGING = True

DEBUG_MODE = True

POOL_SNAPSHOTS = ["mypool"] # Ensure the pools matches the pools used in "take_snapshots.sh"
POOL_SNAPSHOTS_PREFIX = "AS" # Ensure this prefix matches the prefix used in "take_snapshots.sh"

MAX_SNAPSHOT_AGE_IN_DAYS = 1

ZFS_SNAPSHOT_REMOVE_COMMAND = ["zfs", "destroy"]


def log(module, level, message):
	t = datetime.now()
	header = str(t.strftime("%d/%m/%Y %H:%M:%S"))
	
	if COLOUR_LOGGING:
		header = "\033[1;35m%s\033[1;m" % header
		
		
		# Colourise the module
		c1 = "\033[1;36m"
		c2 = "\033[1;m"
		
		module = c1 + module + c2
		
		
		# Colourise the level
		if level == "Information":
			c1 = "\033[1;32m"
			
		elif level == "Warning":
			c1 = "\033[1;33m"
			
		elif level == "Exception" or level == "Error":
			c1 = "\033[1;31m"
			
		else:
			c1 = "\033[1;34m"
		
		level = c1 + level + c2
		
		
		# Colourise the message
		c1 = "\033[1;37m"
		
		message = c1 + message + c2
	
	print "%s/%s()/%s - %s" % (header, module, level, message)

def main():
	try:
		if MAX_SNAPSHOT_AGE_IN_DAYS < 1:
			raise Exception("Max snapshot age must be greater than zero.")
		
		
		log("main", "Information", "Querying DanZFS...")
		
		z = DanZFS(colour_logging = COLOUR_LOGGING, debug_mode = DEBUG_MODE)
		snapshots = z.zfsListSnapshots()
		z.dispose()
		z = None
		
		
		print
		log("main", "Information", "Searching for snapshots at least %d days old..." % MAX_SNAPSHOT_AGE_IN_DAYS)
		
		if snapshots is not None:
			snapshots_to_remove = []
			
			for snapshot in snapshots:
				s = snapshot["name"]
				
				# Snapshots can't be filtered via the command line therefore DanZFS can't do this
				for ps in POOL_SNAPSHOTS:
					if s.startswith("%s@%s-" % (ps, POOL_SNAPSHOTS_PREFIX)):
						snapshot_name = s.split("@")[1]
						
						
						# Ensure it's a valid snapshot date format we're expecting - "PREFIX-yyyyMMdd-HHmm"
						snapshot_datetime = snapshot_name.split("-")
						
						if len(snapshot_datetime) == 3:
							if snapshot_datetime[0] == POOL_SNAPSHOTS_PREFIX and len(snapshot_datetime[1]) == 8 and len(snapshot_datetime[2]) == 4:
								# Grab the date of the snapshot and determine if it's too old - TODO: Also check the time
								snapshot_date = snapshot_datetime[1]
								
								d = date(int(snapshot_date[0:4]), int(snapshot_date[4:6]), int(snapshot_date[6:8]))
								now = date.today()
								
								delta = now - d
								age = delta.days
								
								
								log("main", "Information", "Snapshot %s is %d days old." % (s, age))
								
								if age >= MAX_SNAPSHOT_AGE_IN_DAYS:
									log("main", "Information", "Flagging snapshot %s for deletion..." % s)
									
									snapshots_to_remove.append(s)
								
							else:
								log("main", "Warning", "Ignoring snapshot %s as it doesn't match our criteria." % snapshot_name)
							
						else:
							log("main", "Warning", "Ignoring snapshot %s as it doesn't match our criteria." % snapshot_name)
						
					else:
						log("main", "Warning", "Ignoring snapshot %s as it doesn't match our criteria." % s)
			
			
			# Anything to remove?
			log("main", "Information", "%d snapshots require removal." % len(snapshots_to_remove))
			
			for remove in snapshots_to_remove:
				# Make sure we've got a snapshot - being paranoid...
				if remove.find("@") >= 0:
					try:
						cmd = list(ZFS_SNAPSHOT_REMOVE_COMMAND)
						cmd.append(remove)
						
						
						log("main", "Information", "Removing snapshot %s..." % remove)
						
						p = subprocess.Popen(cmd, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
						stdout, stderr = p.communicate()
						
						p.wait()
						returncode = p.returncode
						p = None
						
						if returncode <> 0:
							log("main", "Warning", "Returned exit code %d." % returncode)
							
							if DEBUG_MODE:
								log("main", "Debug", "STDOUT - %s" % str(stdout))
								log("main", "Debug", "STDERR - %s" % str(stderr))
						
					except Exception, ex2:
						log("main", "Exception", "%s" % str(ex2))
					
				else:
					log("main", "Warning", "Wooah!  %s doesn't appear to be a snapshot." % remove)
			
		else:
			log("main", "Error", "No snapshot data was returned.")
		
	except Exception, ex:
		log("main", "Exception", "%s" % str(ex))


########
# Main #
########
if __name__ == "__main__":
	main()
