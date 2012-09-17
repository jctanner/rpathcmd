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

import xmlrpclib
import shlex
from getpass import getpass
from optparse import Option
from rpathcmd.utils import *

import time
import urllib
import urllib2
import httplib2
from pprint import pprint

from genshi.template import TextTemplate

from xobj import xobj
import epdb

def help_packages_list(self):
    print 'packages_list: list projects'
    print 'usage: packagess_list projectshortname branch stage'

def do_packages_list(self, options):

    h2 = httplib2.Http("~/.rpathcmd/.cache")
    h2.disable_ssl_certificate_validation = True
    h2.add_credentials(self.options.username, self.options.password)

    print "not yet implemented"


def __get_querysetid_by_name(self, name):
    # /api/v1/query_sets;filter_by=[query_set.name,EQUAL,All%20projects]

    h2 = httplib2.Http("~/.rpathcmd/.cache")
    h2.disable_ssl_certificate_validation = True
    h2.add_credentials(self.options.username, self.options.password)        

    #epdb.st()
    filterterm = urllib.quote(name)
    #print "#%s" % filterterm 

    tmpxml = h2.request('http://' + self.options.server + 
                        '/api/v1/query_sets;filter_by=[query_set.name,EQUAL,' +
                        filterterm + ']')
    tmpdata = xobj.parse(tmpxml[1])                     
    #epdb.st()
    print "#%s == %s" % (filterterm, int(tmpdata.query_sets.query_set.query_set_id))
    return int(tmpdata.query_sets.query_set.query_set_id)
    


def help_package_spfimport(self):
    print 'package_spfimport: import an spf package from a url'
    print 'usage package_spfimport projectshortname branchname spfurl spfname spfversion spfextractdir'

def do_package_spfimport(self, args):
    

    maxAttempts = 540
    requestDelay = 1

    # define XMLRPC session
    xmlrpc_endpoint = "https://%s:%s@%s/xmlrpc-private" % (self.options.username, self.options.password, self.options.server)
    self.proxy = xmlrpclib.ServerProxy(xmlrpc_endpoint)

    # set options
    (args, options) = parse_arguments(args)    
    projectshortname = args[0]    
    proj_id = int(__projectshortname_to_id(self, projectshortname))    
    branchname = args[1]    
    branch_id = int(__branchname_to_id(self, projectshortname, branchname))
    rebuild = False
    stage_label = str(__branchname_to_devlabel(self, projectshortname, branchname))
    stage_label = stage_label + '-devel'   

    spfurl = args[2]
    #spfname = args[3]
    #spfversion = args[4]
    #spfextractdir = args[5] 

    # startPackageCreatorSession(self, projectId, prodVer, namespace, troveName, label):

    # start pcreator/appcreator session
    start_appcreator_session_rsp = self.proxy.startApplianceCreatorSession(
                int(proj_id),
                int(branch_id),
                True,
                str(stage_label) )

    epdb.st()

    # output session info
    #pp.pprint(start_appcreator_session_rsp)
    pprint(start_appcreator_session_rsp)
    print "session: %s" % start_appcreator_session_rsp[1][0]
    print "isApplianceCreatorManaged: %s" % start_appcreator_session_rsp[1][1]['isApplianceCreatorManaged']
    sessionToken = start_appcreator_session_rsp[1][0]

    #create temp dir on the rbuilderto push the spf file into
    #epdb.st()
    create_temp_package_dir = self.proxy.createPackageTmpDir()
    print "Temp Package Dir: %s" % create_temp_package_dir
    print "Package URL: %s" % spfurl


    # invoke CGI script with file url and the tempdir ID
    #       file will land in ... /srv/rbuilder/tmp/rb-pc-upload-$ID/tmp_$ID.ccs
    url = 'http://'+self.options.server+'/cgi-bin/urldownloader.cgi?fileUrl='+spfurl+'&uploadId='+create_temp_package_dir[1]
    print "cgiurl: %s" % url
    #upload_file_rsp = restutil.rawGet(url)
    # GET the url, so the cgi runs
    h = httplib2.Http(".cache")
    upload_file_rsp = h.request(url, "GET") 
    #epdb.st()
    pprint(upload_file_rsp)

    # fail if not Ok
    #assert upload_file_rsp == 'Ok\n'
    assert upload_file_rsp[1] == 'Ok\n'


    # get all meta about the imported file
    package_factory_rsp = self.proxy.getPackageFactories(int(proj_id),
                create_temp_package_dir[1],
                int(branch_id),
                '',
                '',
                str(stage_label))

    #epdb.st()

    # parse session
    session_Token = package_factory_rsp [1][0]
    # get factory type
    factoryHandle = package_factory_rsp[1][1][0][0]
    # get contents of defaults.txt
    smartformdetails = package_factory_rsp[1][1][0][1]

    #epdb.st()
    packagemeta = xobj.parse(smartformdetails)
    for field in packagemeta.factory.dataFields.field:
        #epdb.st()
        #print field.name
        '''
        *name --required
        *version --required
        license
        summary
        description
        *location --required
        config_descriptor
        '''
        # required fields, will have <default> elements if set in defaults.txt
        print field.name
        if field.name == 'name':
            spfname = str(field.name)
        if field.name == 'version':
            spfversion == str(field.default)
        if field.name == 'location':
            spfextractdir = str(field.default)

    epdb.st()
    #print package_factory_rsp[1][1][0][1]

    configdata = {  'name': spfname,
                    'version': spfversion,
                    'location': spfextractdir }

    pprint(configdata)
    #epdb.st()

    # getPackageCreateRecipe is "supposed" to return whatever recipe
    #   is in the spf. A default override recipe is returned if
    #   the spf does not include recipe.txt
    packageCreatorRecipeRsp = self.proxy.getPackageCreatorRecipe(session_Token)

    # set the recipe to whatever pcreator returns
    recipe = packageCreatorRecipeRsp[1][1]

    # send back whatever recipe/configdata we have
    save_package_response = self.proxy.savePackage(session_Token,
                                    factoryHandle,
                                    configdata,
                                    True,
                                    recipe)

    pprint(save_package_response)

    # poll job till finished, failure or thresholds met
    for i in range(maxAttempts):

        # fetch status
        package_build_status = self.proxy.getPackageBuildStatus(session_Token)
        now = time.strftime('%Y%m%d%H%M%S')
        print "%s - %s" % (now, package_build_status[1][2])

        if package_build_status[1][0]:
            print "Package build completed"
            print "Package build status: %s" % package_build_status[1][2]

            break
        time.sleep(requestDelay)
    else:
        asserts.fail("Committed state Not reached in :%s seconds" % \
            (maxAttempts * requestDelay))


def __projectshortname_to_id (self, projectshortname):
    #create session 
    h2 = httplib2.Http("~/import_spf/.cache")
    h2.disable_ssl_certificate_validation = True
    h2.add_credentials(self.options.username, self.options.password)

    # request queryset by NAME
    tmpxml =  h2.request('http://' + self.options.server + '/api/v1/projects')

    # find the queryset URL
    tmpdata = xobj.parse(tmpxml[1])
    fullcollectionurl = tmpdata.projects.full_collection

    # filter for specific project name
    fullcollectionurl = fullcollectionurl + ';filter_by=[project.short_name,EQUAL,' + projectshortname + ']'
    fullxml = h2.request(fullcollectionurl)
    fulldata = xobj.parse(fullxml[1])

    # grep the project ID
    project_id = fulldata.projects.project.project_id

    return project_id

def __branchname_to_id (self, projectshortname, branchname):
    #create session 
    h2 = httplib2.Http("~/import_spf/.cache")
    h2.disable_ssl_certificate_validation = True
    h2.add_credentials(self.options.username, self.options.password)

    # api/v1/projects/jt-pcreator/project_branches;filter_by=[name,EQUAL,trunk]
    # request queryset by NAME
    tmpxml =  h2.request('http://' + self.options.server +
                '/api/v1/projects/' + projectshortname +
                '/project_branches;filter_by=[name,EQUAL,' + branchname + ']' )

    tmpdata = xobj.parse(tmpxml[1])

    #epdb.st()

    branch_id = tmpdata.project_branches.project_branch.branch_id
    return branch_id    

def __branchname_to_devlabel (self, projectshortname, branchname):
    #create session 
    h2 = httplib2.Http("~/import_spf/.cache")
    h2.disable_ssl_certificate_validation = True
    h2.add_credentials(self.options.username, self.options.password)

    # api/v1/projects/jt-pcreator/project_branches;filter_by=[name,EQUAL,trunk]
    # request queryset by NAME
    tmpxml =  h2.request('http://' + self.options.server +
                '/api/v1/projects/' + projectshortname +
                '/project_branches;filter_by=[name,EQUAL,' + branchname + ']' )

    tmpdata = xobj.parse(tmpxml[1])

    #epdb.st()

    label = tmpdata.project_branches.project_branch.label
    return label
