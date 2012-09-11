#!/usr/bin/python

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


'''
 627 def _getLatestGroupAppliance(self, auth, project, stage):
 628 logutil.info("_getLatestGroupAppliance")
 629 repository_search = restutil.get(stage.project_branch_stage.groups.href, auth=auth)
 630 matches = helpers.getXpathMatchList(repository_search,
 631 "/troves/trove[name='group-%s-appliance']" % project.project.short_name)
 632 asserts.fail_unless(len(matches) > 0, "Could not find any built group for this product.")
 633 group_versions = [x.trove.trailingVersion for x in matches]
 634 group_versions.sort()
 635 trailing_version = group_versions[-1]
 636 matches = [match for match in matches if match.trove.trailingVersion == trailing_version]
 637 return matches 
 '''

def help_group_create(self):
    print "project_branch_group_create: create a default group" 
    print "     in the Development stage of a group"
    print "usage: project_branch_create projectshortname branchname" 

def do_group_create(self, args):

    '''
    project_id = 26
    branch_id = 42
    rebuild = ??? (True/False) 
    label = shortname-test0001.fe.rpath.com@r:shortname-test0001-trunk-devel
    '''

    xmlrpc_endpoint = "https://%s:%s@%s/xmlrpc-private" % (self.options.username, self.options.password, self.options.server)
    self.proxy = xmlrpclib.ServerProxy(xmlrpc_endpoint)

    #proj_id = 26
    #branch_id = 42
    #rebuild = False
    #stage_label = 'shortname-test0001.fe.rpath.com@r:shortname-test0001-trunk-devel'

    (args, options) = parse_arguments(args)

    projectshortname = args[0]
    #proj_id = self.
    branchname = args[1]
    #branch_id = 
    rebuild = False
    #stage_label = 
    epdb.st()

    # create appcreator session
    sessiondata = self.proxy.startApplianceCreatorSession(proj_id, branch_id, 
                                                          rebuild, stage_label)
    # [False, ['session-tUUlDZ', {'isApplianceCreatorManaged': True}]]
    pcreator_session = sessiondata[1][0]

    # fetch the current/default group recipe
    recipedata = self.proxy.getPackageCreatorRecipe(pcreator_session)
    # [False, [True, '# vim: ts=4 sw=4 expandtab ai\n#\n# rPath, Inc
    recipe = recipedata[1][1]


    # setApplianceTroves('session-6jQT5s', ['ssh-pub-key'])
    # makeApplianceTrove('session-6jQT5s')
    # getPackageBuildStatus('session-6jQT5s')
    #       returned: [False, [False, 4, 'running: Loading 1 troves', []]]
    # getPackageBuildStatus('session-6jQT5s')
    #       returned: [False, [True, 2, 'committed: ',


    # savePackageCreatorRecipe(session, recipe)
    #epdb.st()

    # start group build
    groupbuildstatus = False
    groupbuilddata = self.proxy.makeApplianceTrove(pcreator_session)
    #epdb.st()

    # poll till finished
    while groupbuildstatus == False:
        groupbuilddata = self.proxy.getPackageBuildStatus(pcreator_session)
        groupbuildstatus = groupbuilddata[1][0] 
        print groupbuilddata[1][2] 
        #epdb.st()
        time.sleep(5)


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

    epdb.st()

    branch_id = tmpdata.project_branches.project_branch.branch_id
    return branch_id

