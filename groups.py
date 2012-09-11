#!/usr/bin/python

import xmlrpclib
import shlex
from getpass import getpass
from optparse import Option
from rpathcmd.utils import *
import re

import time
import urllib
import urllib2
import httplib2
from pprint import pprint

from genshi.template import TextTemplate

from xobj import xobj
import epdb

def do_group_argtest(self, args):

    (args, options) = parse_arguments(args)

    epdb.st()


def help_group_list(self):
    print "group_list: list groups in a project branch stage"
    print "usage: group_list projectshortname branchname stage"

def do_group_list(self, args):

    # https://poc3.fe.rpath.com/api/products/shortname-test0001/repos/search?type=group&label=shortname-test0001.fe.rpath.com@r%3Ashortname-test0001-trunk-devel&_method=GET

    #create session 
    h2 = httplib2.Http("~/import_spf/.cache")
    h2.disable_ssl_certificate_validation = True
    h2.add_credentials(self.options.username, self.options.password)
  
    (args, options) = parse_arguments(args) 
    projectshortname = args[0]
    proj_id = int(__projectshortname_to_id(self, projectshortname))
    branchname = args[1]
    branch_id = int(__branchname_to_id(self, projectshortname, branchname))

    #epdb.st()

    stage = args[2]
    stage_label = str(__branchname_to_devlabel(self, projectshortname, branchname))
    stage_label = stage_label + '-' + str(stage)
 
    f = { 'type' : 'group', 'label' : stage_label}
    fields = urllib.urlencode(f)

    #epdb.st()

    # api/v1/projects/jt-pcreator/project_branches;filter_by=[name,EQUAL,trunk]
    # request queryset by NAME
    tmpxml =  h2.request('http://' + self.options.server +
                '/api/products/' + projectshortname +
                '/repos/search?' + fields )

    tmpdata = xobj.parse(tmpxml[1])

    #epdb.st()

    expectedgroupname = "group-" + projectshortname + "-appliance"
    for trove in tmpdata.troves.trove:
        if (str(trove.name) == expectedgroupname):
            print "%s=%s" %(trove.name, trove.version)

def help_group_create(self):
    print "group_create: create a group" 
    print "     in the \"Development\" stage of a project branch"
    print "usage: group_create projectshortname branchname package1,package2,package3" 

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
    proj_id = int(__projectshortname_to_id(self, projectshortname))
    branchname = args[1]
    branch_id = int(__branchname_to_id(self, projectshortname, branchname))
    rebuild = False
    stage_label = str(__branchname_to_devlabel(self, projectshortname, branchname))
    stage_label = stage_label + '-devel'

    packages = args[2]
    packages_list = re.split(r',', packages)

    epdb.st()

    # create appcreator session
    print "starting appcreator session: %s %s %s %s" %(proj_id, branch_id, rebuild, stage_label)
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

    #epdb.st()

    label = tmpdata.project_branches.project_branch.label
    return label

