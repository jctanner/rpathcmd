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

def help_platforms_list(self):
    print 'platforms_list: list projects'
    print 'usage: platforms_list'

def do_platforms_list(self, options):

    # https://qa3.eng.rpath.com/api/platforms 

    '''
    <?xml version='1.0' encoding='UTF-8'?>
    <platforms>
      <platform id="http://poc3.fe.rpath.com/api/platforms/1">
        <platformId>1</platformId>
        <repositoryHostname>rhel.rpath.com</repositoryHostname>
        <label>rhel.rpath.com@rpath:rhel-5-server</label>
        <platformName>Red Hat Enterprise Linux Server 5</platformName>
        <platformUsageTerms>Use of Red Hat Enter ...  Hat.</platformUsageTerms>
        <mode>manual</mode>
        <enabled>false</enabled>
        <configurable>false</configurable>
        <abstract>false</abstract>
        <hidden>false</hidden>
        <mirrorPermission>false</mirrorPermission>
        <repositoryUrl href="http://poc3.fe.rpath.com/repos/rhel.rpath.com/api"/>
        <contentSources href="http://poc3.fe.rpath.com/api/platforms/1/contentSources"/>
        <platformStatus href="http://poc3.fe.rpath.com/api/platforms/1/status"/>
        <contentSourceTypes href="http://poc3.fe.rpath.com/api/platforms/1/contentSourceTypes"/>
        <load href="http://poc3.fe.rpath.com/api/platforms/1/load/"/>
        <imageTypeDefinitions href="http://poc3.fe.rpath.com/api/platforms/1/imageTypeDefinitions"/>
        <platformVersions href="http://poc3.fe.rpath.com/api/platforms/1/platformVersions/"/>
      </platform>
    '''

    h2 = httplib2.Http("~/.rpathcmd/.cache")
    h2.disable_ssl_certificate_validation = True
    h2.add_credentials(self.options.username, self.options.password)    

    tmpxml =  h2.request('http://' + self.options.server + '/api/platforms')

    if (tmpxml[0]['status'] != '200'):
        print "fetching platforms failed: %s" % tmpxml[0]['status']
        sys.exit(1)

    platformdata = xobj.parse(tmpxml[1])

    for platform in platformdata.platforms.platform:
        #epdb.st()
        print "%s: %s, %s" % (platform.platformId, platform.label, platform.platformName)
