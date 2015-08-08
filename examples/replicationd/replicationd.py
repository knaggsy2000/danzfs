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


# Variables
DEBUG_MODE = True


###########
# Classes #
###########
class Replicationd():
	def __init__(self, debug_mode = True):
		from datetime import datetime
		
		import hashlib
		import json
		import os
		import sys
		import time
		
		
		self.datetime = datetime
		self.hashlib = hashlib
		self.json = json
		self.log = DanLog("Replicationd")
		self.os = os
		self.replication_file = None
		self.replication_kill_file = None
		self.sys = sys
		self.time = time
		
		
		# Ensure we have a config file to work on before continuing
		if len(sys.argv) <> 3:
			self.log.error("Invalid number of arguments.")
			
			self.displayUsage()
			self.exit(1)
		
		self.replication_file = self.sys.argv[1]
		self.replication_kill_file = "%s.kill" % self.replication_file
		self.replication_mode = self.sys.argv[2]
		
		if not self.os.path.exists(self.replication_file):
			self.log.error("The configuration file doesn't exist.")
			self.exit(1)
		
		if self.replication_mode not in ["runonce", "start", "stop"]:
			self.log.error("The startup mode '%s' is not recognised." % self.replication_mode)
			self.exit(1)
		
		if self.os.path.exists(self.replication_kill_file):
			self.os.unlink(self.replication_kill_file)
		
		
		self.DEBUG_MODE = debug_mode
		self.REPLICATION_INTERVAL = 15 # How much rest we should give in seconds
		self.REPLICATION_POOLS = self.jsonReadSettings(self.replication_file)
		
		
		# Run the main sub if we are stopping the daemon
		if self.replication_mode == "stop":
			self.main()
		
		
		# Since we support one-to-one and one-to-many replication, we need to create a simple split for everything
		new_replication_pool = []
		
		for p in self.REPLICATION_POOLS:
			self.log.info("Source %s has %d destinations." % (p["Source"], len(p["Destinations"])))
			
			for d in p["Destinations"]:
				n = {}
				n["Source"] = p["Source"]
				n["SourceType"] = p["SourceType"]
				n["Destination"] = d["Destination"]
				n["DestinationType"] = d["DestinationType"]
				
				new_replication_pool.append(n)
		
		self.REPLICATION_POOLS = list(new_replication_pool)
		self.RUNNING_AS_ROOT = False
		
		self.STATE_CLEAN = 0
		self.STATE_REPLICATED = 1
		self.STATE_BUSY = 2
		self.STATE_MISSING = 3
		self.STATE_SNAPSHOT_ISSUE = 4
		self.SNAPSHOT_NAME_BASE = "base"
		self.SNAPSHOT_NAME_INCREMENTAL = "incr"
		self.SNAPSHOT_PREFIX = "RD"
		
		
		# Are we root?
		if self.os.geteuid() == 0:
			self.RUNNING_AS_ROOT = True
			
			self.log.info("We are running with root privileges.")
			
		else:
			self.RUNNING_AS_ROOT = False
			
			self.log.warn("We are NOT running with root privileges, this will mean we can't make any changes to the filesystem (including creating/renaming/destroying/sending/receiving snapshots).")
			self.log.warn("This means that replicationd won't be able to do very much apart from working out the replication state.")
	
	def checksum(self, data):
		return self.hashlib.sha1(data).hexdigest()
	
	def displayUsage(self):
		self.log.info("")
		self.log.info("")
		self.log.info("Usage")
		self.log.info("=====")
		self.log.info("python replicationd.py rd-config.json MODE")
		self.log.info("")
		self.log.info("MODE can be: -")
		self.log.info("  runonce - Performs the replication run only once then exits.")
		self.log.info("  start   - Starts the replicationd daemon.")
		self.log.info("  stop    - Stops the replicationd daemon.")
		self.log.info("")
		self.log.info("*********************************************************************************************************************")
		self.log.info("*** Replicationd has to run with root privileges due to the nature of ZFS.                                        ***")
		self.log.info("***                                                                                                               ***")
		self.log.info("*** Without root privileges we only get \"readonly\" access to the filesystem - but this can be useful for testing. ***")
		self.log.info("*********************************************************************************************************************")
	
	def dispose(self):
		self.log.info("Disposing...")
	
	def exit(self, exitcode = 0):
		self.sys.exit(exitcode)
	
	def getDateTime(self):
		t = self.datetime.now()
		
		return str(t.strftime("%d/%m/%Y %H:%M:%S.%f"))
	
	def jsonReadSettings(self, filename):
		self.log.info("Reading JSON settings file '%s'..." % filename)
		
		
		d = None
		
		with open(filename, "rb") as f:
			d = f.read()
			f.close()
		
		r = self.json.loads(d)
		
		return r
	
	def main(self):
		if self.replication_mode == "runonce":
			self.runOnce()
			
		elif self.replication_mode == "start":
			self.start()
			
		elif self.replication_mode == "stop":
			self.stop()
	
	def rebuildPath(self, p):
		new_path = ""
		
		for s in p:
			if len(new_path) == 0:
				new_path = s
				
			else:
				new_path += "/%s" % s
		
		return new_path
	
	def replicate(self):
		self.log.info("Determining the replication state...")
		
		# Attach extra properties to the replication pools
		for p in self.REPLICATION_POOLS:
			p["CombinedName"] = "%s:%s" % (p["Source"], p["Destination"])
			p["GUID"] = self.checksum(p["CombinedName"])
			p["SnapshotsFound"] = []
			p["State"] = self.STATE_CLEAN
			
			# If we're using ZFS datasets, we need to change the snapshot name
			if p["Source"].find("/") <> -1:
				p["DestinationSnapshotName"] = "%s/%s" % (p["Destination"], self.rebuildPath(p["Source"].split("/")[1:]))
				
			else:
				p["DestinationSnapshotName"] = p["Destination"]
			
			
			if p["SourceType"] is not None and p["DestinationType"] is not None:
				self.log.warn("Pool %s appears to have remote connections for both sides, this is not recommended but will continue." % p["CombinedName"])
		
		
		missing_pools_src = []
		missing_pools_dest = []
		missing_pools_pair = []
		
		for p in self.REPLICATION_POOLS:
			self.log.info("Checking replication pair %s..." % p["CombinedName"])
			
			for s in [[p["Source"], p["SourceType"], "source"], [p["Destination"], p["DestinationType"], "destination"]]:
				self.log.info("Checking pool %s if exists..." % s[0])
				
				z = DanZFS(remote_command = s[1], debug_mode = self.DEBUG_MODE)
				pools = z.zfsListFilesystems(s[0])
				z.dispose()
				z = None
				
				if pools is not None:
					if len(pools) == 0:
						self.log.error("The %s pool %s does not exist." % (s[2], s[0]))
						
						if s[2] == "source":
							missing_pools_src.append(s[0])
							
						elif s[2] == "destination":
							missing_pools_dest.append(s[0])
						
						
						if not p["CombinedName"] in missing_pools_pair:
							missing_pools_pair.append(p["CombinedName"])
					
				else:
					self.log.error("An error has occurred while checking the %s pool %s." % (s[2], s[0]))
					
					if s[2] == "source":
						missing_pools_src.append(s[0])
						
					elif s[2] == "destination":
						missing_pools_dest.append(s[0])
					
					
					if not p["CombinedName"] in missing_pools_pair:
						missing_pools_pair.append(p["CombinedName"])
		
		
		# Grab the snapshots (if there are any) and determine what state we are in
		self.log.info("Querying the replication state from the snapshots...")
		
		snapshots = []
		
		for p in self.REPLICATION_POOLS:
			if not p["CombinedName"] in missing_pools_pair:
				for s in [[p["Source"], p["SourceType"], "src"], [p["DestinationSnapshotName"], p["DestinationType"], "dest"]]:
					skip = False
					
					if s[2] == "src":
						skip = s[0] in missing_pools_src
						
					elif s[2] == "dest":
						skip = s[0] in missing_pools_dest
					
					
					if not skip:
						z = DanZFS(remote_command = s[1], debug_mode = self.DEBUG_MODE)
						snaps = z.zfsListSnapshots()
						z.dispose()
						z = None
						
						if snaps is not None:
							for e in snaps:
								# Ensure we only bring back what we're looking for
								if s[2] == "src":
									if e["name"].startswith("%s@" % p["Source"]):
										snapshots.append(e)
									
								elif s[2] == "dest":
									if e["name"].startswith("%s@" % p["DestinationSnapshotName"]):
										snapshots.append(e)
				
			else:
				# Part of the pool has gone missing, ignore it for now
				p["State"] = self.STATE_MISSING
				
				self.log.error("Pool %s has gone missing, not querying the snapshot status." % p["CombinedName"])
		
		
		# We should all the data we need, work it out...
		self.log.info("Determining the replication state from the snapshots...")
		
		if snapshots is not None:
			for snapshot in snapshots:
				s = snapshot["name"]
				
				for p in self.REPLICATION_POOLS:
					if not p["CombinedName"] in missing_pools_pair:
						if s.startswith("%s@%s-" % (p["Source"], self.SNAPSHOT_PREFIX)) or s.startswith("%s@%s-" % (p["DestinationSnapshotName"], self.SNAPSHOT_PREFIX)):
							snapshot_name = s.split("@")[1]
							
							
							# Ensure it's a valid snapshot format we're expecting - "PREFIX-GUID-X"
							snapshot_datetime = snapshot_name.split("-")
							
							if len(snapshot_datetime) == 3:
								if snapshot_datetime[0] == self.SNAPSHOT_PREFIX and snapshot_datetime[1] == p["GUID"] and (snapshot_datetime[2] == self.SNAPSHOT_NAME_BASE or snapshot_datetime[2] == self.SNAPSHOT_NAME_INCREMENTAL):
									if s not in p["SnapshotsFound"]:
										p["SnapshotsFound"].append(s)
										p["State"] = self.STATE_REPLICATED
									
									
									if snapshot_datetime[2] == self.SNAPSHOT_NAME_INCREMENTAL:
										p["State"] = self.STATE_BUSY
										
										self.log.warn("Snapshot %s is an incremental, normally we shouldn't see this." % snapshot_name)
									
								else:
									self.log.warn("Ignoring snapshot %s as it doesn't match our criteria." % snapshot_name)
								
							else:
								self.log.warn("Ignoring snapshot %s as it doesn't match our criteria." % snapshot_name)
							
						else:
							self.log.warn("Ignoring snapshot %s as it doesn't match our criteria." % s)
			
		else:
			self.log.warn("No snapshot data was returned.")
		
		
		# Check what state each of the pools are in so we know where to start
		for p in self.REPLICATION_POOLS:
			if not p["State"] in [self.STATE_MISSING]:
				if len(p["SnapshotsFound"]) == 0 or len(p["SnapshotsFound"]) == 2:
					# Clean or replication-state
					pass
					
				elif len(p["SnapshotsFound"]) == 1:
					# Inconsistent
					p["State"] = self.STATE_SNAPSHOT_ISSUE
					
					self.log.error("Pool %s appears to have an odd number of RD snapshots (%d found), cannot continue as the state won't be known correctly." % (p["CombinedName"], len(p["SnapshotsFound"])))
					
				else:
					# Numerous snapshots found
					p["State"] = self.STATE_SNAPSHOT_ISSUE
					
					self.log.error("Pool %s appears to have multiple RD snapshots (%d found), cannot continue as the state won't be known correctly." % (p["CombinedName"], len(p["SnapshotsFound"])))
			
			
			if p["State"] == self.STATE_CLEAN:
				self.log.warn("Pool %s is in a clean state." % p["CombinedName"])
				
			elif p["State"] == self.STATE_REPLICATED:
				self.log.info("Pool %s is in replication state." % p["CombinedName"])
				
			elif p["State"] == self.STATE_BUSY:
				self.log.warn("Pool %s is currently replicating." % p["CombinedName"])
				
			elif p["State"] == self.STATE_MISSING:
				self.log.error("Pool %s is currently missing, please investigate." % p["CombinedName"])
				
			elif p["State"] == self.STATE_SNAPSHOT_ISSUE:
				self.log.error("Pool %s has snapshot issues, please investigate and correct them (most likely you will need to either rename or destroy one more of them)." % p["CombinedName"])
				
			else:
				self.log.error("Pool %s is in unknown state." % p["CombinedName"])
		
		
		
		self.log.info("The replication state has now been determined.")
		
		# Create all the snapshots first so we have consistent snapshots across all the destination boxes
		con_snap = {}
		
		for p in self.REPLICATION_POOLS:
			if p["State"] == self.STATE_CLEAN or p["State"] == self.STATE_REPLICATED:
				if p["State"] == self.STATE_CLEAN:
					self.log.info("Pool %s is in a clean state, generating base snapshot..." % p["CombinedName"])
					
				elif p["State"] == self.STATE_REPLICATED:
					self.log.info("Pool %s is in replication state, generating incremental snapshot..." % p["CombinedName"])
				
				
				snapshot_name = "%s@%s-%s" % (p["Source"], self.SNAPSHOT_PREFIX, p["GUID"])
				
				if p["State"] == self.STATE_CLEAN:
					snapshot_name = "%s-%s" % (snapshot_name, self.SNAPSHOT_NAME_BASE)
					
				elif p["State"] == self.STATE_REPLICATED:
					snapshot_name = "%s-%s" % (snapshot_name, self.SNAPSHOT_NAME_INCREMENTAL)
				
				
				z = DanZFS(remote_command = p["SourceType"], debug_mode = self.DEBUG_MODE)
				
				if not z.zfsCreateSnapshot(snapshot_name):
					raise Exception("Failed to create the snapshot, cannot continue.")
				
				z.dispose()
				z = None
				
				
				con_snap[p["CombinedName"]] = snapshot_name
		
		
		# Now perform the replication
		results = {}
		
		for p in self.REPLICATION_POOLS:
			try:
				results[p["CombinedName"]] = {}
				results[p["CombinedName"]]["Started"] = self.getDateTime()
				
				
				if p["State"] == self.STATE_CLEAN or p["State"] == self.STATE_REPLICATED:
					
					if p["CombinedName"] in con_snap:
						snapshot_name = con_snap[p["CombinedName"]]
						
						results[p["CombinedName"]]["Snapshot"] = snapshot_name.split("@")[1].replace("-%s" % self.SNAPSHOT_NAME_BASE, "").replace("-%s" % self.SNAPSHOT_NAME_INCREMENTAL, "")
						
						if p["State"] == self.STATE_CLEAN:
							r = ["-dF", p["Destination"]]
							s = [snapshot_name]
							
							z1 = DanZFS(remote_command = p["SourceType"], debug_mode = self.DEBUG_MODE)
							z2 = DanZFS(remote_command = p["DestinationType"], debug_mode = self.DEBUG_MODE)
							
							if not z2.zfsReceive(r, z1.zfsSend(s)):
								raise Exception("Failed to send the data to the destination, cannot continue.")
							
							z1.dispose()
							z2.dispose()
							
							z1 = None
							z2 = None
							
							
							results[p["CombinedName"]]["Status"] = "OK"
							results[p["CombinedName"]]["Type"] = "Full"
							
						elif p["State"] == self.STATE_REPLICATED:
							s = None
							r = ["-dF", p["Destination"]]
							
							for a in p["SnapshotsFound"]:
								s = ["-i", a, snapshot_name]
								
								if a.startswith("%s@%s-" % (p["Source"], self.SNAPSHOT_PREFIX)) and a.endswith(self.SNAPSHOT_NAME_BASE):
									z1 = DanZFS(remote_command = p["SourceType"], debug_mode = self.DEBUG_MODE)
									z2 = DanZFS(remote_command = p["DestinationType"], debug_mode = self.DEBUG_MODE)
									
									if not z2.zfsReceive(r, z1.zfsSend(s)):
										raise Exception("Failed to send the data to the destination, cannot continue.")
									
									z1.dispose()
									z2.dispose()
									
									z1 = None
									z2 = None
									
									
									break # Should only be one
							
							
							# We need to switch around the snapshots to become the new base
							self.log.info("Destroying the old base snapshots...")
							
							for a in p["SnapshotsFound"]:
								if a.startswith("%s@%s-" % (p["Source"], self.SNAPSHOT_PREFIX)) and a.endswith(self.SNAPSHOT_NAME_BASE):
									self.log.info("Destroying the %s snapshot..." % a)
									
									
									z = DanZFS(remote_command = p["SourceType"], debug_mode = self.DEBUG_MODE)
									
									if not z.zfsDestroySnapshot(a):
										raise Exception("Failed to destroy the snapshot, cannot continue.")
									
									z.dispose()
									z = None
									
								elif a.startswith("%s@%s-" % (p["DestinationSnapshotName"], self.SNAPSHOT_PREFIX)) and a.endswith(self.SNAPSHOT_NAME_BASE):
									self.log.info("Destroying the %s snapshot..." % a)
									
									
									z = DanZFS(remote_command = p["DestinationType"], debug_mode = self.DEBUG_MODE)
									
									if not z.zfsDestroySnapshot(a):
										raise Exception("Failed to destroy the snapshot, cannot continue.")
									
									z.dispose()
									z = None
							
							
							self.log.info("Renaming the snapshots...")
							
							
							z = DanZFS(remote_command = p["SourceType"], debug_mode = self.DEBUG_MODE)
							
							if not z.zfsRenameSnapshot(snapshot_name, snapshot_name.replace(self.SNAPSHOT_NAME_INCREMENTAL, self.SNAPSHOT_NAME_BASE)):
								raise Exception("Failed to rename the source snapshot, cannot continue.")
							
							z.dispose()
							z = None
							
							
							z = DanZFS(remote_command = p["DestinationType"], debug_mode = self.DEBUG_MODE)
							
							if not z.zfsRenameSnapshot(snapshot_name.replace("%s@" % p["Source"], "%s@" % p["DestinationSnapshotName"]), snapshot_name.replace("%s@" % p["Source"], "%s@" % p["DestinationSnapshotName"]).replace(self.SNAPSHOT_NAME_INCREMENTAL, self.SNAPSHOT_NAME_BASE)):
								raise Exception("Failed to rename the destination snapshot, cannot continue.")
							
							z.dispose()
							z = None
							
							
							self.log.info("Pool %s has been replicated." % p["CombinedName"])
							
							
							results[p["CombinedName"]]["Status"] = "OK"
							results[p["CombinedName"]]["Type"] = "Incremental"
						
					else:
						self.log.error("Cannot find the consistent snapshot for pool %s, exiting." % p["CombinedName"])
						self.exit(1)
					
				else:
					results[p["CombinedName"]]["Type"] = ""
					results[p["CombinedName"]]["Snapshot"] = ""
					
					
					if p["State"] == self.STATE_BUSY:
						# Busy
						results[p["CombinedName"]]["Status"] = "Busy"
						
						self.log.warn("Pool %s is currently replicating, will not attempt to start another." % p["CombinedName"])
						
					elif p["State"] == self.STATE_MISSING:
						# Missing
						results[p["CombinedName"]]["Status"] = "Missing"
						
						self.log.warn("Pool %s is missing, will not attempt to start." % p["CombinedName"])
						
					elif p["State"] == self.STATE_SNAPSHOT_ISSUE:
						# Snapshot issue
						results[p["CombinedName"]]["Status"] = "Snapshot Issues"
						
						self.log.warn("Pool %s has snapshot issues, will not attempt to start." % p["CombinedName"])
						
					else:
						# Unknown
						results[p["CombinedName"]]["Status"] = "Unknown"
						
						self.log.error("Pool %s is in unknown state." % p["CombinedName"])
				
				
				results[p["CombinedName"]]["Finished"] = self.getDateTime()
				
			except Exception, ex:
				self.log.error("An error has occurred while replicating pool %s." % p["CombinedName"])
				self.log.error(ex)
				
				results[p["CombinedName"]]["Status"] = "Failure"
				results[p["CombinedName"]]["Type"] = ""
				results[p["CombinedName"]]["Snapshot"] = ""
				results[p["CombinedName"]]["Finished"] = self.getDateTime()
		
		
		self.log.info("")
		self.log.info("")
		self.log.info("Replication Report")
		self.log.info("==================")
		
		for r in results.keys():
			o = results[r]
			
			
			self.log.info(r)
			self.log.info("^" * len(r))
			
			if o["Status"] == "OK":
				self.log.info("Status:   %s" % o["Status"])
				
			elif o["Status"] == "Busy":
				self.log.warn("Status:   %s" % o["Status"])
				
			else:
				self.log.error("Status:   %s" % o["Status"])
			
			self.log.info("Type:     %s" % o["Type"])
			self.log.info("Snapshot: %s" % o["Snapshot"])
			self.log.info("Started:  %s" % o["Started"])
			self.log.info("Finished: %s" % o["Finished"])
			self.log.info("")
	
	def runOnce(self):
		self.log.info("Running once...")
		
		try:
			self.replicate()
			
		except Exception, ex:
			self.log.error(ex)
			
		finally:
			self.exit(0)
	
	def start(self):
		self.log.info("Starting daemon...")
		
		while True:
			try:
				self.replicate()
				
			except Exception, ex:
				self.log.error(ex)
				
			except KeyboardInterrupt:
				self.log.info("Keyboard interrupt, exiting...")
				self.exit(0)
				
			finally:
				# Make the daemon shutdown a bit faster is we have a long replication interval
				for x in xrange(0, self.REPLICATION_INTERVAL):
					if self.os.path.exists(self.replication_kill_file):
						self.log.info("Kill file detected for this configuration, exiting...")
						
						self.os.unlink(self.replication_kill_file)
						self.exit(0)
						
					else:
						try:
							self.log.info("Sleeping for %02d/%02d seconds..." % (self.REPLICATION_INTERVAL - x, self.REPLICATION_INTERVAL))
							
							self.time.sleep(1)
							
						except KeyboardInterrupt:
							self.log.info("Keyboard interrupt, exiting...")
							self.exit(0)
	
	def stop(self):
		self.log.info("Creating kill file for the running configuration...")
		
		self.touchFile(self.replication_kill_file)
		
		self.log.info("The kill file has been created, the daemon will exit after its next replication run, please be patient.  Exiting...")
		self.exit(0)
	
	def touchFile(self, filename):
		with open(filename, "wb") as f:
			f.close()


def main():
	try:
		r = Replicationd()
		r.main()
		r.dispose()
		r = None
		
	except Exception, ex:
		print str(ex)


########
# Main #
########
if __name__ == "__main__":
	main()
