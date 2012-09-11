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

import pdb
#from utils import restutil
#from utils import xmlrpcutils
from lxml import etree
import xml.etree.ElementTree as ET
import time
import urllib
import urllib2
import httplib2
from pprint import pprint
import xml.dom.minidom

import xmltodict
#import yaml
#import BeautifulSoup

def help_api_versions(self):
    print 'api_versions: list api versions'
    print 'usage: api_versions'

def do_api_versions(self, options):
    # http://$RBA/api
    '''
    <?xml version='1.0' encoding='UTF-8'?>
    <api>
        <api_versions>
            <api_version id="http://ciscorba.eng.rpath.com/api/v1" description="rBuilder REST API version 1" name="v1"/>
        </api_versions>
    </api>
    '''
    #self.options.server
    #self.options.username
    #self.options.password
    #self.options.debug

    h2 = httplib2.Http("~/.rpathcmd/.cache")
    h2.disable_ssl_certificate_validation = True
    h2.add_credentials(self.options.username, self.options.password)
    
    apixml =  h2.request('http://' + self.options.server + '/api')
    if apixml[0]['status'] != '304':
        print "error: %s" % apixml[0]['status']
        print "response: %s" % apixml[1]
        sys.exit(1)

    #pdb.set_trace()
    doc = xmltodict.parse(apixml[1])
    pprint(doc)

    '''
    roots = ET.fromstring(apixml[1])
    for root in roots:
        for child in root:
            #pdb.set_trace()
            pprint(child.tag)
            pprint(child.attrib)
    '''

def help_api_v1_info(self):
    print 'api_v1_info: list api/v1 info'
    print 'usage: api_v1_info'

def do_api_v1_info(self, options):
    h2 = httplib2.Http("~/.rpathcmd/.cache")
    h2.disable_ssl_certificate_validation = True
    h2.add_credentials(self.options.username, self.options.password)

    apixml = h2.request('http://' + self.options.server + '/api/v1')
    if apixml[0]['status'] != '304':
        print "error: %s" % apixml[0]['status']
        print "response: %s" % apixml[1]
        sys.exit(1)

    #pdb.set_trace()
    #doc = xmltodict.parse(apixml[1])
    doc = xmltodict.parse(str(apixml[1]))
    pprint(doc)
    #pdb.set_trace()

    '''
    roots = ET.fromstring(apixml[1])
    for root in roots:
        for child in root:
            #pdb.set_trace()
            pprint(child.tag)
            pprint(child.attrib)
    '''
