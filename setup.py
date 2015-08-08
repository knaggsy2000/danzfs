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


from distutils.core import setup


APP_NAME = "danzfs"
APP_VERSION = "0.2.0"


setup(
	name = APP_NAME,
	version = APP_VERSION,
	author = "Daniel Knaggs",
	author_email = "knaggsy2000@gmail.com",
	url = "http://code.google.com/p/%s/" % APP_NAME,
	description = "Provides a Python API for interacting with ZFS without using libzfs",
	long_description = """DanZFS provides a Python API for checking the status of ZFS without the use of
libzfs by calling the system binaries and parsing the output.

Currently you can: -

1. List the ZFS properties (name, property, value, source)
2. List filesystems, snapshots, and volumes (name, used, available, refer, and
mountpoint)
3. Query the pool IO statistics (name, capacity, operations, and bandwidth)
4. List the pools (name, size, allocated, free, capacity, deduplication, health,
and alternativeroot)
5. Query the pool status (name, state, status, action, scan, config-type,
config-disks, and errors)
6. Replication via snapshots both locally and via SSH

The data from the API calls will be returned as a Python dictionary.""",
	download_url = "http://%s.googlecode.com/files/%s-%s.tar.xz" % (APP_NAME, APP_NAME, APP_VERSION),
	py_modules = [APP_NAME],
	classifiers = [
		"Development Status :: 3 - Alpha",
		"Environment :: Console",
		"Intended Audience :: Developers",
		"Intended Audience :: End Users/Desktop",
		"Intended Audience :: System Administrators",
		"License :: OSI Approved :: BSD License",
		"Operating System :: POSIX",
		"Operating System :: POSIX :: BSD",
		"Operating System :: POSIX :: BSD :: FreeBSD",
		"Operating System :: POSIX :: BSD :: NetBSD",
		"Operating System :: POSIX :: BSD :: OpenBSD",
		"Operating System :: POSIX :: Linux",
		"Operating System :: POSIX :: SunOS/Solaris",
		"Operating System :: Unix",
		"Programming Language :: Python",
		"Topic :: System",
		"Topic :: System :: Filesystems",
		"Topic :: System :: Monitoring",
		"Topic :: System :: Systems Administration",
		"Topic :: Utilities",
	]
)
