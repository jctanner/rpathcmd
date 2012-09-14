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
    #epdb.st()

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
    
    # setup pretty printing
    #pp = pprint.PrettyPrinter(indent=4)

    maxAttempts = 540
    requestDelay = 1

    # define XMLRPC session
    xmlrpc_endpoint = "https://%s:%s@%s/xmlrpc-private" % (self.options.username, self.options.password, self.options.server)
    self.proxy = xmlrpclib.ServerProxy(xmlrpc_endpoint)

    (args, options) = parse_arguments(args)    
    projectshortname = args[0]    
    proj_id = int(__projectshortname_to_id(self, projectshortname))    
    branchname = args[1]    
    branch_id = int(__branchname_to_id(self, projectshortname, branchname))
    rebuild = False
    stage_label = str(__branchname_to_devlabel(self, projectshortname, branchname))
    stage_label = stage_label + '-devel'   

    spfurl = args[2]
    spfname = args[3]
    spfversion = args[4]
    spfextractdir = args[5] 


    # A DEFAULT RECIPE
    recipe ="""
    class OverrideRecipe(FactoryRecipeClass):
     \tdef postProcess(r):
      \t\t'''This function is run at the end of setup'''"""

    # SET PACKAGE INFO JUST LIKE IN UI AFTER IMPORTING URL
    configdata = {  'name': spfname,
                    'version': spfversion,
                    'manufacturer': 'rPath',
                    'applicationType': 'app',
                    'location': spfextractdir,
                    'summary': 'rpathcmd imported spf',
                    'description': 'rpathcmd imported spf' }    

    # start pcreator/appcreator session
    #start_appcreator_session_rsp = xmlrpcclient.start_appcreator_session(
    start_appcreator_session_rsp = self.proxy.startApplianceCreatorSession(
                int(proj_id),
                int(branch_id),
                False,
                str(stage_label) )

    # output session info
    #pp.pprint(start_appcreator_session_rsp)
    pprint(start_appcreator_session_rsp)
    print "session: %s" % start_appcreator_session_rsp[1][0]
    print "isApplianceCreatorManaged: %s" % start_appcreator_session_rsp[1][1]['isApplianceCreatorManaged']
    sessionToken = start_appcreator_session_rsp[1][0]

    #create temp dir on the rbuilderto push the spf file into
    #create_temp_package_dir = xmlrpcclient.create_temp_package_dir()
    create_temp_package_dir = self.proxy.createPackageTmpDir()
    print "Temp Package Dir: %s" % create_temp_package_dir
    print "Package URL: %s" % spfurl


    # invoke CGI script with file url and the tempdir ID
    #       file will land in ... /srv/rbuilder/tmp/rb-pc-upload-$ID/tmp_$ID.ccs
    url = 'http://'+rba+'/cgi-bin/urldownloader.cgi?fileUrl='+pkgurl+'&uploadId='+create_temp_package_dir[1]
    print "cgiurl: %s" % url
    upload_file_rsp = restutil.rawGet(url)
    #pp.pprint(upload_file_rsp)
    pprint(upload_file_rsp)

    # fail if not Ok
    assert upload_file_rsp == 'Ok\n'


    # tell pcreator to start the build
    #package_factory_rsp = xmlrpcclient.get_package_Factories(int(proj_id),
    package_factory_rsp = self.proxy.getPackageFactories(int(proj_id),
                create_temp_package_dir[1],
                int(branch_id),
                str(label))


    # output response
    #pp.pprint(package_factory_rsp)
    session_Token = package_factory_rsp [1][0]
    factoryHandle = package_factory_rsp[1][1][0][0]

    # DO NOT UNDERSTAND THIS ... not sure if necessary
    #packageCreatorRecipeRsp = xmlrpcclient.get_package_creator_recipe(username,password,session_Token)
    packageCreatorRecipeRsp = self.proxy.getPackageCreatorRecipe(username,password,session_Token)

    # send over the recipe and config data
    #save_package_response = xmlrpcclient.save_Package(session_Token,factoryHandle,configdata,recipe)
    save_package_response = self.proxy.savePackage(session_Token,factoryHandle,configdata,recipe)


    # poll job till finished, failure or thresholds met
    for i in range(maxAttempts):

        # fetch status
        #package_build_status = xmlrpcclient.get_package_status(session_Token)
        package_build_status = self.proxy.getPackageBuildStatus(session_Token)
        #pp.pprint(package_build_status[1][2])
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
