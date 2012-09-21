#
# Licensed under the GNU General Public License Version 3
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.


import shlex
from getpass import getpass
from optparse import Option
from rpathcmd.utils import *

import time
import urllib
import urllib2
import httplib2
from pprint import pprint


from xobj import xobj
import epdb


def help_targets_list(self):
    print 'images_list: list all images'
    print 'usage: images_list'

def do_targets_list(self, options):

    h2 = httplib2.Http("~/.rpathcmd/.cache")
    h2.disable_ssl_certificate_validation = True
    h2.add_credentials(self.options.username, self.options.password)

    #a list of each page's xml
    images_data_pages = []

    # fetch first page, save and parse 
    tmpxml =  h2.request('http://' + self.options.server + '/api/v1/targets')
    images_data_pages.append(tmpxml[1])
    tmpdata = xobj.parse(tmpxml[1])

    #epdb.st()

    if len(tmpdata.targets.target) == 0:
        print "%s: %s" % (tmpdata.targets.target.target_id, tmpdata.targets.target.name)
    else:
        for target in tmpdata.targets.target:
            print "%s: %s" % (target.target_id, target.name)

