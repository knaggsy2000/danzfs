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


def main():
	try:
		print "Information: Querying DanZFS..."
		
		z = DanZFS(debug_mode = DEBUG_MODE)
		pools = z.zfsPoolIOStat() # You can also pass a specific pool name if you want, no argument will return everything
		z.dispose()
		z = None
		
		
		if pools is not None:
			print "Information: Displaying pool information..."
			print
			print
			
			print "Number of Pools: %d" % len(pools)
			print
			
			for pool in pools:
				print "Pool:               %s" % pool["pool"]
				print "Capacity Allocated: %s" % pool["capacity"]["allocated"]
				print "Capacity Free:      %s" % pool["capacity"]["free"]
				print "Operations Read:    %s" % pool["operations"]["read"]
				print "Operations Write:   %s" % pool["operations"]["write"]
				print "Bandwidth Read:     %s" % pool["bandwidth"]["read"]
				print "Bandwidth Write:    %s" % pool["bandwidth"]["write"]
				
				print
			
		else:
			print "Error: No pool data was returned."
		
	except Exception, ex:
		print str(ex)


########
# Main #
########
if __name__ == "__main__":
	main()
