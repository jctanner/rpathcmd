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

# rest stuff
import time
import urllib
import urllib2
import httplib2
from pprint import pprint
from urllib import urlencode

# parsing/debugging
from xobj import xobj
import epdb

# templating
from genshi.template import TextTemplate
import ast

    
def help_systems_list(self):
    print 'systems_list: list all systems'
    print 'usage: systems_list'

def do_systems_list(self, options):

    h2 = httplib2.Http("~/.rpathcmd/.cache")
    h2.disable_ssl_certificate_validation = True
    h2.add_credentials(self.options.username, self.options.password)

    #a list of each page's xml
    systems_data_pages = []
 
    # fetch first page, save and parse 
    tmpxml =  h2.request('http://' + self.options.server + '/api/v1/inventory/systems')
    systems_data_pages.append(tmpxml[1])
    tmpdata = xobj.parse(tmpxml[1])

    #epdb.st()
    # to paginate or not to paginate, that is the question.
    if int(tmpdata.systems.num_pages) == 1:
        print "#one page"
    else:
        print "%s pages" % tmpdata.systems.num_pages
        next_page_url = tmpdata.systems.next_page
        while next_page_url != '':
            # fetch next page
            print "fetching %s" % next_page_url
            #nextxml = h2.request(tmpdata.systems.next_page)
            nextxml = h2.request(next_page_url)
            # save data
            systems_data_pages.append(nextxml[1])
            # parse xml
            nextdata = xobj.parse(nextxml[1])
            # check next page
            next_page_url = nextdata.systems.next_page
            #epdb.st()

    #epdb.st()
    for systems_data_page in systems_data_pages:
        systems_data = xobj.parse(systems_data_page)
        #epdb.st()
        for system in systems_data.systems.system:
            #epdb.st()

            name = system.name
            id = system.system_id
            state = system.current_state.name
            owner = system.launching_user

            ip = "NULL"
            if hasattr(system, "network_address"):
                ip = system.network_address.address


            print "%s: %s %s %s %s" %(id, name, ip, state, owner)
    
def help_system_info(self):
    print 'system_info: show information about a system'
    print 'usage: system_info [id]'

def do_system_info(self, options):


    # input validation ... TBD :(
    system_id = options


    #epdb.st()

    h2 = httplib2.Http("~/.rpathcmd/.cache")
    h2.disable_ssl_certificate_validation = True
    h2.add_credentials(self.options.username, self.options.password)

    #a list of each page's xml
    systems_data_pages = []
 
    # fetch first page, save and parse 
    tmpxml =  h2.request('http://' + self.options.server + '/api/v1/inventory/systems/' + system_id)
    systems_data_pages.append(tmpxml[1])
    tmpdata = xobj.parse(tmpxml[1])

    #epdb.st()
    #system.name = tmpdata.system.name

    print "url: " + tmpdata.system.id
    print "id: " + tmpdata.system.system_id
    print "name: " + tmpdata.system.name
    print "uuid: " + tmpdata.system.generated_uuid
    print "ipaddress: " + tmpdata.system.network_address.address
    print "createdby: " + tmpdata.system.created_by
    print "hostname: " + tmpdata.system.hostname
    print "launchdate: " + tmpdata.system.launch_date
    print "launchuser: " + tmpdata.system.launching_user
    print "project: " + tmpdata.system.project.short_name
    print "branch: " + tmpdata.system.project_branch.name
    print "stage: " + tmpdata.system.project_branch_stage.name
    print "trove: " + tmpdata.system.observed_top_level_items.observed_top_level_item.trove_spec 
    print "sourceimage: " + tmpdata.system.source_image.id
    print "surveys: " + tmpdata.system.surveys
    print "type: " + tmpdata.system.system_type
    print "target: " + tmpdata.system.target
    print "targetstate: " + tmpdata.system.target_system_state
    print "rbastate: " + tmpdata.system.current_state.name
    print "latestsurvey: " + tmpdata.system.latest_survey.id


def help_system_group_update(self):
    print 'system_group_update: update the group on a single system'
    print '''usage: system_group_update [SYSTEMID] [TROVE]'''


def do_system_group_update(self, args):

    (args, options) = parse_arguments(args)

    system_id = args[0]
    trove = args[1]

    #epdb.st()

    '''
    updateXml = self._generateUpdateXml(system, currentVersionTrove, updateVersion)
    installedSoftware = restutil.put(system.system.installed_software.id,
                auth=auth, data=updateXml)
    '''

    '''
    https://qa3.eng.rpath.com/api/v1/inventory/event_types/26
    <name>system update software</name>
    '''

    # add credentials
    h2 = httplib2.Http("~/.rpathcmd/.cache")
    h2.disable_ssl_certificate_validation = True
    h2.add_credentials(self.options.username, self.options.password)

    # find the event_type id that == 'system update software'
    tmpxml =  h2.request('http://' + self.options.server + '/api/v1/inventory/event_types')
    tmpdata = xobj.parse(tmpxml[1])

    update_event_id = "NULL"
    for event_type in tmpdata.event_types.event_type:
        #print ""
        #print event_type.name
        if event_type.name == "system update software":
            update_event_id = event_type.job_type_id    
    #epdb.st()


   
    #templatefile = '/usr/lib/python2.6/site-packages/rpathcmd/xml/system_group_update_template.xml'
    #templatefile = '/usr/lib64/python2.6/site-packages/rpathcmd/xml/system_group_update_template.xml'
    moduledir = os.path.dirname(self.sys.modules['rpathcmd.systems'].__file__)
    xmldir = moduledir + '/xml/'
    templatefile = xmldir + 'system_group_update_template.xml'
    templatedata = open(templatefile, 'r')

    # RBA_HOSTNAME
    # SYSTEM_ID
    # TROVE_LABEL
   
    #system_id = 100 
    #trove = 'group-blah-blah-blah'
    #system_id = 209
    #trove = 'group-wells-weblogic-rpath-poc2-appliance=/wells-weblogic-rpath-poc2.fe.rpath.com@r:wells-weblogic-rpath-poc2-stateA-devel/stateA-8-1'

    values = {  'RBA': self.options.server,
                'EVENT_ID': update_event_id, 
                'SYSTEM_ID': system_id, 
                'TROVE': trove}
    #epdb.st()
    '''
    # not sure why values needs to be casted as string,
    # but ast says "malformed string" otherwise
    datadict = ast.literal_eval(str(values))
    '''

    #epdb.st()

    template = TextTemplate(templatedata, lookup='lenient')
    #stream = template.generate(**datadict)
    stream = template.generate(**values)
    postxml = stream.render('text')

    print "########## <POSTDATA> ##########"
    print postxml
    #pprint(postxml)
    print "########## ^POSTDATA^ ##########"

    #h.request("http://bitworking.org/news/223/Meet-Ares", "POST", urlencode(data))
    jobxml =  h2.request('http://' + self.options.server + 
                            '/api/v1/inventory/systems/' + str(system_id) + '/jobs',
                            headers={'Content-Type': 'application/xml'},
                            method="POST", 
                            body=postxml)

    print ""
    pprint(jobxml)

    if jobxml[0]['status'] != '200':
        print "job failed: %s" % jobxml[0]['status']
        sys.exit(1)

    jobdata = xobj.parse(jobxml[1])

    #epdb.st()

    job_url = jobdata.job.id
    job_status = jobdata.job.status_text
    job_status_code = jobdata.job.status_code

    '''
    while ((job_status != "Done") or 
            (job_status_code != "404") or 
            (job_status != 'Failed')):
    '''
    while ((job_status != "Done") and 
            (job_status != "Failed") and
            (job_status_code != '430')): 
        jobxml = h2.request(job_url)
        jobdata = xobj.parse(jobxml[1])
        job_status = jobdata.job.status_text
        job_status_code = jobdata.job.status_code
        print job_status
        #epdb.st()
        time.sleep(2)


