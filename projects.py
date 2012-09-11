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

def help_projects_list(self):
    print 'projects_list: list projects'
    print 'usage: projects_list'

def do_projects_list(self, options):

    h2 = httplib2.Http("~/.rpathcmd/.cache")
    h2.disable_ssl_certificate_validation = True
    h2.add_credentials(self.options.username, self.options.password)

    projectsdatapages = []
  
    tmpxml =  h2.request('http://' + self.options.server + '/api/v1/projects')
    projectsdatapages.append(tmpxml[1])

    tmpdata = xobj.parse(tmpxml[1])

    if int(tmpdata.projects.num_pages) == 1:
        print "#one page"
    else:
        print "pagination not yet supported"
        sys.exit(1)

    for projectsdatapage in projectsdatapages:
        projectsdata = xobj.parse(projectsdatapage)
        for project in projectsdata.projects.project:
            #epdb.st()

            # some projects do not have user_names,
            #   so handle that correctly
            user_name = "NULL"
            if hasattr(project.created_by, "user_name"):
                user_name =  project.created_by.user_name

            print "%s: %s %s" % (project.project_id, user_name, project.short_name)

    
def help_project_branches_list(self):
    print 'project_branches_list: list project branches'
    print 'usage: project_branches_list'

def do_project_branches_list(self, options):

    h2 = httplib2.Http("~/.rpathcmd/.cache")
    h2.disable_ssl_certificate_validation = True
    h2.add_credentials(self.options.username, self.options.password)

    branchesdatapages = []
  
    tmpxml =  h2.request('http://' + self.options.server + '/api/v1/project_branches')
    branchesdatapages.append(tmpxml[1])

    tmpdata = xobj.parse(tmpxml[1])

    #epdb.st()
    if int(tmpdata.project_branches.num_pages) == 1:
        print "#one page"
    else:
        print "pagination not yet supported"
        sys.exit(1)

    for branchesdatapage in branchesdatapages:
        branchesdata = xobj.parse(branchesdatapage)
        for project_branch in branchesdata.project_branches.project_branch:
            #epdb.st()
            print "%s: %s %s" % (project_branch.branch_id, 
                                project_branch.project.short_name, 
                                project_branch.name)

    
def help_project_branch_stages_list(self):
    print 'project_branche_stages_list: list project branch stages'
    print 'usage: project_branch_stages_list'

def do_project_branch_stages_list(self, options):

    h2 = httplib2.Http("~/.rpathcmd/.cache")
    h2.disable_ssl_certificate_validation = True
    h2.add_credentials(self.options.username, self.options.password)

    stages_data_pages = []
  
    tmpxml =  h2.request('http://' + self.options.server + '/api/v1/project_branch_stages')
    stages_data_pages.append(tmpxml[1])

    tmpdata = xobj.parse(tmpxml[1])

    #epdb.st()
    if int(tmpdata.project_branch_stages.num_pages) == 1:
        print "#one page"
    else:
        print "%s pages" % tmpdata.project_branch_stages.num_pages
        next_page_url = tmpdata.project_branch_stages.next_page
        while next_page_url != '':
            # fetch next page
            print "fetching %s" % next_page_url
            nextxml = h2.request(tmpdata.project_branch_stages.next_page)
            # save data
            stages_data_pages.append(nextxml[1])
            # parse xml
            nextdata = xobj.parse(nextxml[1])
            # check next page
            next_page_url = nextdata.project_branch_stages.next_page
            #epdb.st()

    for stages_data_page in stages_data_pages:
        stages_data = xobj.parse(stages_data_page)
        #epdb.st()
        for stage in stages_data.project_branch_stages.project_branch_stage:
            #epdb.st()
            project = stage.project.short_name
            branch = stage.project_branch.name
           
            print "%s __ %s %s %s" %(stage.label, project, branch, stage.name) 


def help_project_create(self):
    print "project_create: create a new project"
    print "usage: project_create name shortname"    

def do_project_create(self, args):
   
    # https://qa3.eng.rpath.com/api/v1/projects
    # POST XML ... project_template.xml

    # $NAME
    # $SHORT_NAME

    print "not done"
    moduledir = os.path.dirname(self.sys.modules['rpathcmd.systems'].__file__)
    xmldir = moduledir + '/xml/'
    templatefile = xmldir + 'project_template.xml'
    templatedata = open(templatefile, 'r')

    (args, options) = parse_arguments(args)
    projectname = args[0]
    projectshortname = args[1]

    values = {  'NAME': projectname,
                'SHORT_NAME': projectshortname}

    template = TextTemplate(templatedata, lookup='lenient')
    stream = template.generate(**values)
    postxml = stream.render('text')
    print "########## <POSTDATA> ##########"
    print postxml
    print "########## ^POSTDATA^ ##########"    


    # initialize httlib2 and add credentials
    h2 = httplib2.Http("~/.rpathcmd/.cache")
    h2.disable_ssl_certificate_validation = True
    h2.add_credentials(self.options.username, self.options.password)

    # make POST request
    returndata = h2.request('http://' + self.options.server +
                            '/api/v1/projects',
                            headers={'Content-Type': 'application/xml'},
                            method="POST",
                            body=postxml)

    #pprint(returndata)
    if returndata[0]['status'] != '200':
        print "creation failed: %s" % returndata[0]['status']
        sys.exit(1)
    else:
        print "creation completed: %s" % returndata[0]['status']


    returnxml = xobj.parse(returndata[1])
    #epdb.st()
    print "projectid: %s" % returnxml.project.project_id
    print "name: %s" % returnxml.project.name
    print "shortname: %s" % returnxml.project.short_name
    print "hostname: %s" % returnxml.project.hostname





def help_project_branch_create(self):
    print "project_branch_create: create a new project branch"
    print "usage: project_branch_create project_shortname branch_name platformid platformlabel"    

def do_project_branch_create(self, args):
   
    # https://qa3.eng.rpath.com/api/platforms 
    # https://$RBA/api/v1/projects/test-centos6-automation2-1347312349/project_branches
    # POST XML ... project_branch_template.xml

    # $PROJECT_SHORTNAME
    # $BRANCH_NAME
    # $RBA
    # $PLATFORM_LABEL
    # $PLATFORM_ID

    moduledir = os.path.dirname(self.sys.modules['rpathcmd.systems'].__file__)
    xmldir = moduledir + '/xml/'
    templatefile = xmldir + 'project_branch_template.xml'
    templatedata = open(templatefile, 'r')

    (args, options) = parse_arguments(args)
    projectshortname = args[0]
    branch_name = args[1]
    platform_id = args[2]
    platform_label = args[3]

    values = {  'RBA': self.options.server,
                'PROJECT_SHORTNAME': projectshortname,
                'PLATFORM_ID': platform_id,
                'PLATFORM_LABEL': platform_label,
                'BRANCH_NAME': branch_name}

    template = TextTemplate(templatedata, lookup='lenient')
    stream = template.generate(**values)
    postxml = stream.render('text')
    print "-----------<POSTDATA>-----------"
    print postxml
    print "-----------<POSTDATA>-----------" 

    # initialize httlib2 and add credentials
    h2 = httplib2.Http("~/.rpathcmd/.cache")
    h2.disable_ssl_certificate_validation = True
    h2.add_credentials(self.options.username, self.options.password)

    # make POST request
    returndata = h2.request('http://' + self.options.server +
                            '/api/v1/projects/' + str(projectshortname) + '/project_branches',
                            headers={'Content-Type': 'application/xml'},
                            method="POST",
                            body=postxml)

    #epdb.st()
    #pprint(returndata)
    if returndata[0]['status'] != '200':
        print "creation failed: %s" % returndata[0]['status']
        sys.exit(1)
    else:
        print "creation completed: %s" % returndata[0]['status']


    returnxml = xobj.parse(returndata[1])
    #epdb.st()
    print "projectid: %s" % returnxml.project_branch.project.id
    print "projectshortname: %s" % returnxml.project_branch.project.short_name
    print "branchid: %s" % returnxml.project.project_id
    print "branchname: %s" % returnxml.project_branch.name
    print "label: %s" % returnxml.project_branch.label
    print "platformlabel: %s" % returnxml.project_branch.platform_label
   


def help_project_branch_imagedef_list(self):
    print "project_branch_imagedef_list: list imagedefs for a project branch"
    print "usage: project_branch_imagedef_list project_shortname branch_name"


def do_project_branch_imagedef_list(self, args):    

    # create REST session 
    h2 = httplib2.Http("~/import_spf/.cache")
    h2.disable_ssl_certificate_validation = True
    h2.add_credentials(self.options.username, self.options.password)

    (args, options) = parse_arguments(args)
    projectshortname = args[0]
    branchname = args[1]

    tmpxml =  h2.request('http://' + self.options.server +
                '/api/products/' + projectshortname +
                '/versions/' + branchname + '/imageDefinitions' )    
    tmpdata = xobj.parse(tmpxml[1])    

    epdb.st()
    if isinstance(tmpdata.imageDefinitions.imageDefinition, object):
        print tmpdata.imageDefinitions.imageDefinition.container.name
        print tmpdata.iamgeDefinitions.imageDefinition.architecture.name
    else:    
        for imagedef in tmpdata.imageDefinitions.imageDefinition:
            print imagedef.container.name    
            print imagedef.architecture.name    


 
def help_project_branch_imagedef_create(self):
    print "project_branch_imagedef_create: create " 
    print "     a project branch image definition (64bit vmware only)"
    print "usage: project_branch_imagedef_create"
    print "     project_shortname branch_name freespace"    

def do_project_branch_imagedef_create(self, args):
   
    # https://$RBA/api/products/$PROJECT_SHORTNAME/versions/1.0/imageTypeDefinitions
    # PUT XML ... imagedef-esx-x86.template

    # $RBA
    # $PROJECT_SHORTNAME
    # $FREESPACE == 1024 (MB)

    moduledir = os.path.dirname(self.sys.modules['rpathcmd.systems'].__file__)
    xmldir = moduledir + '/xml/'
    templatefile = xmldir + 'imagedef-esx-x8664.template'
    templatedata = open(templatefile, 'r')

    (args, options) = parse_arguments(args)
    projectshortname = args[0]
    branch_name = args[1]
    freespace = args[2]

    values = {  'RBA': self.options.server,
                'PROJECT_SHORTNAME': projectshortname,
                'BRANCH_NAME': branch_name,
                'FREESPACE': freespace}

    template = TextTemplate(templatedata, lookup='lenient')
    stream = template.generate(**values)
    postxml = stream.render('text')


    print "-----------<POSTDATA>-----------"
    print postxml
    print "-----------<POSTDATA>-----------"

    # initialize httlib2 and add credentials
    h2 = httplib2.Http("~/.rpathcmd/.cache")
    h2.disable_ssl_certificate_validation = True
    h2.add_credentials(self.options.username, self.options.password)

    # make POST request
    returndata = h2.request('http://' + self.options.server +
                            '/api/products/' + str(projectshortname) + 
                            '/versions/' + branch_name + '/imageDefinitions',
                            headers={'Content-Type': 'application/xml'},
                            method="PUT",
                            body=postxml)

    #epdb.st()
    #pprint(returndata)
    if returndata[0]['status'] != '200':
        print "creation failed: %s" % returndata[0]['status']
        sys.exit(1)
    else:
        print "creation completed: %s" % returndata[0]['status']


    returnxml = xobj.parse(returndata[1])
    print returnxml
    #epdb.st()


