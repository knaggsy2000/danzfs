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


###########
# Classes #
###########
class DanLog():
	def __init__(self, header, file_appender = False, colour_logging = True):
		from datetime import datetime
		
		import inspect
		import sys
		
		
		self.datetime = datetime
		self.inspect = inspect
		self.sys = sys
		
		
		self.file_appender = file_appender
		
		
		self.COLOUR_LOGGING = colour_logging
		self.DEBUG = "Debug"
		self.ERROR = "Error"
		self.FATAL = "Fatal"
		self.HEADER = header
		self.INFO = "Info"
		self.WARN = "Warn"
		
		
		self.info("Displaying license for DanLog...")
		self.info("""
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
""")
		
		self.info("DanLog has been initialised.")
	
	def debug(self, message, newline = True):
		self.log(self.DEBUG, message, newline)
	
	def error(self, message, newline = True):
		self.log(self.ERROR, message, newline)
	
	def exit(self, exitcode = 0):
		self.sys.exit(exitcode)
	
	def fatal(self, message, newline = True):
		self.log(self.FATAL, message, newline)
	
	def getCurrentDateTime(self):
		t = self.datetime.now()
		
		return str(t.strftime("%d/%m/%Y %H:%M:%S.%f"))
	
	def info(self, message, newline = True):
		self.log(self.INFO, message, newline)
	
	def log(self, level, message, newline = True):
		t = self.getCurrentDateTime()
		header = self.HEADER
		message = str(message)
		
		
		stack = self.inspect.stack()
		stack1 = stack[1]
		stack2 = stack[2]
		
		caller = stack2[1]
		
		s1 = stack1[3]
		s2 = stack2[3]
		
		
		module = ""
		
		if s2.startswith("<"):
			module = s1
			
		else:
			module = s2
		
		module += "()"
		
		original_module = module
		
		
		colour_output = ""
		normal_output = "%s/%s/%s/%s - %s\n" % (t, header, module, level, message)
		
		if self.COLOUR_LOGGING:
			t = "\033[1;30m%s\033[1;m" % t
			
			header = "\033[1;35m%s\033[1;m" % header
			
			
			c1 = "\033[1;36m"
			c2 = "\033[1;m"
			
			module = c1 + module + c2
			
			
			if level == self.INFO:
				c1 = "\033[1;32m"
				
			elif level == self.WARN:
				c1 = "\033[1;33m"
				
			elif level == self.ERROR:
				c1 = "\033[1;31m"
				
			elif level == self.FATAL:
				c1 = "\033[0;31m"
				
			elif level == self.DEBUG:
				c1 = "\033[1;34m"
			
			level = level.ljust(5)
			level = c1 + level + c2
			
			
			c1 = "\033[1;37m"
			
			message = c1 + str(message) + c2
			
			
			colour_output = "%s/%s/%s/%s - %s\n" % (t, header, module, level, message)
		
		
		if not newline:
			colour_output = colour_output[0:-1]
			normal_output = normal_output[0:-1]
		
		
		# Send the output to the appenders
		if self.COLOUR_LOGGING:
			self.sys.stdout.write(colour_output)
			
		else:
			self.sys.stdout.write(normal_output)
		
		self.sys.stdout.flush()
		
		
		if self.file_appender:
			with open("%s.log" % caller, "a") as f:
				f.write(normal_output)
				f.flush()
				f.close()
	
	def warn(self, message, newline = True):
		self.log(self.WARN, message, newline)

class DanZFS():
	def __init__(self, remote_command = None, colour_logging = True, debug_mode = False):
		import subprocess
		import sys
		
		
		self.log = DanLog("DanZFS")
		self.subprocess = subprocess
		self.sys = sys
		
		self.COLOUR_LOGGING = colour_logging
		self.DEBUG_MODE = debug_mode
		self.EXECUTABLE_ZFS = "zfs"
		self.EXECUTABLE_ZPOOL = "zpool"
		self.REMOTE_COMMAND = remote_command
		self.VERSION = "0.2.0"
		self.ZFS_CREATE = [self.EXECUTABLE_ZFS, "create"]
		self.ZFS_DESTROY = [self.EXECUTABLE_ZFS, "destroy"]
		self.ZFS_GET = [self.EXECUTABLE_ZFS, "get", "all"]
		self.ZFS_RENAME = [self.EXECUTABLE_ZFS, "rename"]
		self.ZFS_LIST_FILESYSTEMS = [self.EXECUTABLE_ZFS, "list", "-t", "filesystem"]
		self.ZFS_LIST_SNAPSHOTS = [self.EXECUTABLE_ZFS, "list", "-t", "snapshot"]
		self.ZFS_LIST_VOLUMES = [self.EXECUTABLE_ZFS, "list", "-t", "volume"]
		self.ZFS_RECEIVE = [self.EXECUTABLE_ZFS, "receive"]
		self.ZFS_SEND = [self.EXECUTABLE_ZFS, "send"]
		self.ZFS_SET = [self.EXECUTABLE_ZFS, "set"]
		self.ZFS_SNAPSHOT = [self.EXECUTABLE_ZFS, "snapshot"]
		self.ZPOOL_DISK_LINE_OFFSET = 2
		self.ZPOOL_KEYWORD_ACTION = "action:"
		self.ZPOOL_KEYWORD_CONFIG = "config:"
		self.ZPOOL_KEYWORD_ERRORS = "errors:"
		self.ZPOOL_KEYWORD_POOL = "pool:"
		self.ZPOOL_KEYWORD_SCAN = "scan:"
		self.ZPOOL_KEYWORD_SEE = "see:"
		self.ZPOOL_KEYWORD_STATE = "state:"
		self.ZPOOL_KEYWORD_STATUS = "status:"
		self.ZPOOL_KEYWORDS = [self.ZPOOL_KEYWORD_ACTION, self.ZPOOL_KEYWORD_CONFIG, self.ZPOOL_KEYWORD_ERRORS, self.ZPOOL_KEYWORD_POOL, self.ZPOOL_KEYWORD_SCAN, self.ZPOOL_KEYWORD_SEE, self.ZPOOL_KEYWORD_STATE, self.ZPOOL_KEYWORD_STATUS]
		self.ZPOOL_IOSTAT = [self.EXECUTABLE_ZPOOL, "iostat"]
		self.ZPOOL_LIST = [self.EXECUTABLE_ZPOOL, "list"]
		self.ZPOOL_STATUS = [self.EXECUTABLE_ZPOOL, "status"]
		
		
		self.log.info("Displaying copyright/license...")
		
		print """
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
"""
		
		
		# Welcome
		self.log.info("Welcome to DanZFS v%s." % self.VERSION)
		
		# Python version checking
		self.log.info("Checking Python version...")
		
		pyv = self.sys.version_info
		self.log.info("Running under Python v%d.%d.%d." % (pyv[0], pyv[1], pyv[2]))
	
	def convertLocalToRemote(self, local_cmd):
		remote_cmd = []
		
		cmd = ""
		
		for c in local_cmd:
			cmd += "%s " % c
		
		for c in self.REMOTE_COMMAND:
			remote_cmd.append(c.replace("${cmd}", cmd.strip()))
		
		return remote_cmd
	
	def dispose(self):
		if self.DEBUG_MODE:
			self.log.info("Running...")
		
		
		self.subprocess = None
		self.sys = None
	
	def run(self, cmd, stdin = None):
		if self.DEBUG_MODE:
			self.log.info("Running %s..." % cmd)
		
		
		p = self.subprocess.Popen(cmd, stdin = self.subprocess.PIPE, stdout = self.subprocess.PIPE, stderr = self.subprocess.PIPE)
		stdout, stderr = p.communicate(stdin)
		
		p.wait()
		returncode = p.returncode
		p = None
		
		
		if self.DEBUG_MODE and returncode <> 0:
			self.log.info("Returned exit code %d." % returncode)
		
		return [stdout, stderr, returncode]
	
	def runPipe(self, cmd1, cmd2):
		if self.DEBUG_MODE:
			self.log.info("Running %s | %s..." % (cmd1, cmd2))
		
		
		p1 = self.subprocess.Popen(cmd1, stdout = self.subprocess.PIPE, stderr = self.subprocess.PIPE)
		p2 = self.subprocess.Popen(cmd2, stdin = p1.stdout, stdout = self.subprocess.PIPE, stderr = self.subprocess.PIPE)
		stdout, stderr = p2.communicate()
		
		p2.wait()
		returncode = p2.returncode
		
		p1 = None
		p2 = None
		
		
		if self.DEBUG_MODE and returncode <> 0:
			self.log.info("Returned exit code %d." % returncode)
			self.log.warn("Stderr: %s" % stderr)
		
		return [stdout, stderr, returncode]
	
	def trimExcessiveSpaces(self, data):
		if self.DEBUG_MODE:
			self.log.info("Running...")
		
		
		ret = str(data)
		
		while ret.find("  ") <> -1:
			ret = ret.replace("  ", " ")
		
		return ret
	
	def zfsCreateSnapshot(self, snapshot):
		if self.DEBUG_MODE:
			self.log.info("Running...")
		
		
		if snapshot.find("@") <> -1:
			cmd = list(self.ZFS_SNAPSHOT)
			cmd.append(snapshot)
			
			if self.REMOTE_COMMAND is not None:
				cmd = self.convertLocalToRemote(cmd)
			
			
			stdout, stderr, returncode = self.run(cmd)
			
			return returncode == 0
			
		else:
			raise Exception("You haven't correctly defined a snapshot name to create.")
	
	def zfsDestroySnapshot(self, snapshot):
		if self.DEBUG_MODE:
			self.log.info("Running...")
		
		
		if snapshot.find("@") <> -1:
			cmd = list(self.ZFS_DESTROY)
			cmd.append(snapshot)
			
			if self.REMOTE_COMMAND is not None:
				cmd = self.convertLocalToRemote(cmd)
			
			
			stdout, stderr, returncode = self.run(cmd)
			
			return returncode == 0
			
		else:
			raise Exception("You haven't correctly defined a snapshot name to destroy.")
	
	def zfsGet(self, specific = ""):
		if self.DEBUG_MODE:
			self.log.info("Running...")
		
		
		cmd = list(self.ZFS_GET)
		
		if specific <> "":
			cmd.append(specific)
		
		if self.REMOTE_COMMAND is not None:
			cmd = self.convertLocalToRemote(cmd)
		
		
		stdout, stderr, returncode = self.run(cmd)
		
		lines = stdout.split("\n")
		
		if len(lines) == 0:
			raise Exception("There doesn't appear to be anything returned.")
			
		else:
			if lines[0].startswith("no pools available"):
				raise Exception("No pools are available.")
				
			else:
				if self.DEBUG_MODE:
					for l in lines:
						self.log("zfsGet", "Debug", l)
				
				
				properties = []
				property = None
				
				num = 0
				
				
				# Clean up the data first
				cleaned = []
				
				for l in lines:
					l = self.trimExcessiveSpaces(l).replace("\t", "").strip()
					cleaned.append(l)
				
				lines = cleaned
				cleaned = None
				
				
				for l in lines:
					if not l.startswith("NAME PROPERTY VALUE SOURCE"):
						d = l.split(" ")
						
						if len(d) == 4:
							property = {"name": d[0], "property": d[1], "value": d[2], "source": d[3]}
							properties.append(property)
				
				
				if self.DEBUG_MODE:
					self.log.debug(str(properties))
				
				return properties
	
	def zfsList(self, command, specific = ""):
		if self.DEBUG_MODE:
			self.log.info("Running...")
		
		
		cmd = list(command)
		
		if specific <> "":
			cmd.append(specific)
		
		if self.REMOTE_COMMAND is not None:
			cmd = self.convertLocalToRemote(cmd)
		
		
		stdout, stderr, returncode = self.run(cmd)
		
		lines = stdout.split("\n")
		
		if len(lines) == 0:
			raise Exception("There doesn't appear to be anything returned.")
			
		else:
			if lines[0].startswith("no pools available"):
				raise Exception("No pools are available.")
				
			else:
				if self.DEBUG_MODE:
					for l in lines:
						self.log.debug(l)
				
				
				datasets = []
				dataset = None
				
				num = 0
				
				
				# Clean up the data first
				cleaned = []
				
				for l in lines:
					l = self.trimExcessiveSpaces(l).replace("\t", "").strip()
					cleaned.append(l)
				
				lines = cleaned
				cleaned = None
				
				
				for l in lines:
					if not l.startswith("NAME USED AVAIL REFER MOUNTPOINT"):
						d = l.split(" ")
						
						if len(d) == 5:
							dataset = {"name": d[0], "used": d[1], "available": d[2], "refer": d[3], "mountpoint": d[4]}
							datasets.append(dataset)
				
				
				if self.DEBUG_MODE:
					self.log.debug(str(datasets))
				
				return datasets
	
	def zfsListEverything(self, specific = ""):
		ret = []
		
		for fs in self.zfsList(self.ZFS_LIST_FILESYSTEMS, specific):
			ret.append(fs)
		
		for ss in self.zfsList(self.ZFS_LIST_SNAPSHOTS):
			ret.append(ss)
		
		for vol in self.zfsList(self.ZFS_LIST_VOLUMES):
			ret.append(vol)
		
		return ret
	
	def zfsListFilesystems(self, specific = ""):
		return self.zfsList(self.ZFS_LIST_FILESYSTEMS, specific)
	
	def zfsListSnapshots(self):
		return self.zfsList(self.ZFS_LIST_SNAPSHOTS)
	
	def zfsListVolumes(self):
		return self.zfsList(self.ZFS_LIST_VOLUMES)
	
	def zfsPoolIOStat(self, specific = ""):
		if self.DEBUG_MODE:
			self.log.info("Running...")
		
		
		cmd = list(self.ZPOOL_IOSTAT)
		
		if specific <> "":
			cmd.append(specific)
		
		if self.REMOTE_COMMAND is not None:
			cmd = self.convertLocalToRemote(cmd)
		
		
		stdout, stderr, returncode = self.run(cmd)
		
		lines = stdout.split("\n")
		
		if len(lines) == 0:
			raise Exception("There doesn't appear to be anything returned.")
			
		else:
			if lines[0].startswith("no pools available"):
				raise Exception("No pools are available.")
				
			else:
				if self.DEBUG_MODE:
					for l in lines:
						self.log.debug(l)
				
				
				pools = []
				pool = None
				
				num = 0
				
				
				# Clean up the data first
				cleaned = []
				
				for l in lines:
					l = self.trimExcessiveSpaces(l).replace("\t", "").strip()
					cleaned.append(l)
				
				lines = cleaned
				cleaned = None
				
				
				for l in lines:
					if not l.startswith("pool alloc free read write read write") and not l.startswith("-"):
						d = l.split(" ")
						
						if len(d) == 7:
							pool = {"pool": d[0], "capacity": {"allocated": d[1], "free": d[2]}, "operations": {"read": d[3], "write": d[4]}, "bandwidth": {"read": d[5], "write": d[6]}}
							pools.append(pool)
				
				
				if self.DEBUG_MODE:
					self.log.debug(str(pools))
				
				return pools
	
	def zfsPoolList(self, specific = ""):
		if self.DEBUG_MODE:
			self.log.info("Running...")
		
		
		cmd = list(self.ZPOOL_LIST)
		
		if specific <> "":
			cmd.append(specific)
		
		if self.REMOTE_COMMAND is not None:
			cmd = self.convertLocalToRemote(cmd)
		
		
		stdout, stderr, returncode = self.run(cmd)
		
		lines = stdout.split("\n")
		
		if len(lines) == 0:
			raise Exception("There doesn't appear to be anything returned.")
			
		else:
			if lines[0].startswith("no pools available"):
				raise Exception("No pools are available.")
				
			else:
				if self.DEBUG_MODE:
					for l in lines:
						self.log.debug(l)
				
				
				pools = []
				pool = None
				
				num = 0
				
				
				# Clean up the data first
				cleaned = []
				
				for l in lines:
					l = self.trimExcessiveSpaces(l).replace("\t", "").strip()
					cleaned.append(l)
				
				lines = cleaned
				cleaned = None
				
				
				for l in lines:
					if not l.startswith("NAME SIZE ALLOC FREE CAP DEDUP HEALTH ALTROOT"):
						d = l.split(" ")
						
						if len(d) == 8:
							pool = {"name": d[0], "size": d[1], "allocated": d[2], "free": d[3], "capacity": d[4], "deduplication": d[5], "health": d[6], "alternativeroot": d[7]}
							pools.append(pool)
				
				
				if self.DEBUG_MODE:
					self.log.debug(str(pools))
				
				return pools
	
	def zfsPoolStatus(self, specific = ""):
		if self.DEBUG_MODE:
			self.log.info("Running...")
		
		
		cmd = list(self.ZPOOL_STATUS)
		
		if specific <> "":
			cmd.append(specific)
		
		if self.REMOTE_COMMAND is not None:
			cmd = self.convertLocalToRemote(cmd)
		
		
		stdout, stderr, returncode = self.run(cmd)
		
		lines = stdout.split("\n")
		
		if len(lines) == 0:
			raise Exception("There doesn't appear to be anything returned.")
			
		else:
			if lines[0].startswith("no pools available"):
				raise Exception("No pools are available.")
				
			else:
				if self.DEBUG_MODE:
					for l in lines:
						self.log.debug(l)
				
				
				pools = []
				pool = None
				
				num = 0
				
				
				# Clean up the data first
				cleaned = []
				
				for l in lines:
					l = self.trimExcessiveSpaces(l).replace("\t", "").strip()
					cleaned.append(l)
				
				lines = cleaned
				cleaned = None
				
				
				for l in lines:
					# Keyword searching
					if l.find(self.ZPOOL_KEYWORD_POOL) <> -1:
						# New pool
						if self.DEBUG_MODE:
							self.log.info("Pool found.")
						
						pool = {"pool": "", "state": "", "status": "", "action": "", "see": "", "scan": "", "config": {"type": "", "disks": []}, "errors": ""}
					
					for k in self.ZPOOL_KEYWORDS:
						if l.find(k) <> -1:
							self.log.debug("%s keyword found." % k)
							
							
							k = k.replace(":", "")
							val = l.split(": ")
							
							if len(val) == 2:
								pool[k] = val[1]
								
								
								# Status runs on multiple lines
								if k == "status":
									num3 = 1
									done = False
									line_once = False
									
									while True:
										m = lines[num + num3]
										
										for kk in self.ZPOOL_KEYWORDS:
											if m.find(kk) == -1:
												if not line_once:
													pool[k] += " "
													pool[k] += m
													
													line_once = True
												
											else:
												done = True
												break
										
										
										if done:
											break
										
										line_once = False
										num3 += 1
					
					
					# Grab the type of pool
					if l.startswith("NAME STATE READ WRITE CKSUM"):
						pool["config"]["type"] = lines[num + self.ZPOOL_DISK_LINE_OFFSET].split(" ")[0].split("-")[0]
						
						# Grab the disks
						disks = []
						disk = None
						num2 = 1
						
						while True:
							m = lines[num + num2 + self.ZPOOL_DISK_LINE_OFFSET]
							
							if m.strip() == "":
								break
								
							else:
								d = m.split(" ")
								
								if len(d) == 5:
									# Disk appears normal
									disk = {"device": d[0], "state": d[1], "read": d[2], "write": d[3], "checksum": d[4]}
									disks.append(disk)
									
								elif len(d) == 7:
									# Disk likely to be offline
									disk = {"device": d[6], "state": d[1], "read": d[2], "write": d[3], "checksum": d[4]}
									disks.append(disk)
							
							num2 += 1
						
						pool["config"]["disks"] = disks
					
					
					if l.find(self.ZPOOL_KEYWORD_ERRORS) <> -1:
						pools.append(pool)
					
					self.log.info(repr(l))
					
					
					num += 1
				
				
				if self.DEBUG_MODE:
					self.log.debug(str(pools))
				
				return pools
	
	def zfsReceive(self, receive, send):
		if self.DEBUG_MODE:
			self.log.info("Running...")
		
		
		cmd = list(self.ZFS_RECEIVE)
		
		for a in receive:
			cmd.append(a)
		
		
		if self.REMOTE_COMMAND is not None:
			cmd = self.convertLocalToRemote(cmd)
		
		
		p1 = self.subprocess.Popen(send, stdout = self.subprocess.PIPE, stderr = self.subprocess.PIPE)
		p2 = self.subprocess.Popen(cmd, stdin = p1.stdout, stdout = self.subprocess.PIPE, stderr = self.subprocess.PIPE)
		stdout, stderr = p2.communicate()
		
		p2.wait()
		returncode = p2.returncode
		
		p1 = None
		p2 = None
		
		
		if self.DEBUG_MODE and returncode <> 0:
			self.log.info("Returned exit code %d." % returncode)
			self.log.warn("Stderr: %s" % stderr)
		
		return returncode == 0
	
	def zfsRenameSnapshot(self, old_snapshot, new_snapshot):
		if self.DEBUG_MODE:
			self.log.info("Running...")
		
		
		if old_snapshot.find("@") <> -1 and new_snapshot.find("@") <> -1:
			cmd = list(self.ZFS_RENAME)
			cmd.append(old_snapshot)
			cmd.append(new_snapshot)
			
			if self.REMOTE_COMMAND is not None:
				cmd = self.convertLocalToRemote(cmd)
			
			
			stdout, stderr, returncode = self.run(cmd)
			
			return returncode == 0
			
		else:
			raise Exception("You haven't correctly defined a snapshot name to rename.")
	
	def zfsSend(self, send):
		if self.DEBUG_MODE:
			self.log.info("Running...")
		
		
		cmd = list(self.ZFS_SEND)
		
		for a in send:
			cmd.append(a)
		
		
		if self.REMOTE_COMMAND is not None:
			cmd = self.convertLocalToRemote(cmd)
		
		return cmd
	
	def zfsSet(self, name, value):
		if self.DEBUG_MODE:
			self.log.info("Running...")
		
		
		cmd = list(self.ZFS_SET)
		cmd.append("%s=\"%s\"" %  (name, value))
		
		if self.REMOTE_COMMAND is not None:
			cmd = self.convertLocalToRemote(cmd)
		
		
		stdout, stderr, returncode = self.run(cmd)
		
		return returncode == 0
