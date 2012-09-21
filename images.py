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

import yaml
import unicodedata

    
def help_images_list(self):
    print 'images_list: list all images'
    print 'usage: images_list'

def do_images_list(self, options):

    h2 = httplib2.Http("~/.rpathcmd/.cache")
    h2.disable_ssl_certificate_validation = True
    h2.add_credentials(self.options.username, self.options.password)

    #a list of each page's xml
    images_data_pages = []
 
    # fetch first page, save and parse 
    tmpxml =  h2.request('http://' + self.options.server + '/api/v1/images')
    images_data_pages.append(tmpxml[1])
    tmpdata = xobj.parse(tmpxml[1])

    #epdb.st()
    # to paginate or not to paginate, that is the question.
    if int(tmpdata.images.num_pages) == 1:
        print "#one page"
    else:
        print "%s pages" % tmpdata.images.num_pages
        next_page_url = tmpdata.images.next_page
        while next_page_url != '':
            # fetch next page
            print "fetching %s" % next_page_url
            nextxml = h2.request(tmpdata.images.next_page)
            # save data
            images_data_pages.append(nextxml[1])
            # parse xml
            nextdata = xobj.parse(nextxml[1])
            # check next page
            next_page_url = nextdata.images.next_page
            #epdb.st()

    #epdb.st()
    for images_data_page in images_data_pages:
        images_data = xobj.parse(images_data_page)
        #epdb.st()
        for image in images_data.images.image:
            #epdb.st()

            #print "%s: %s %s=%s" %(image.image_id, image.name, image.trove_name, image.trove_version)
            print "%s: %s %s=%s" %(image.image_id, image.name, image.trove_name, image.trailing_version )


    



def help_image_info(self):
    print 'image_info: show information about an image'
    print 'usage: image_info [id]'

def do_image_info(self, options):


    # input validation ... TBD :(
    image_id = options


    #epdb.st()

    h2 = httplib2.Http("~/.rpathcmd/.cache")
    h2.disable_ssl_certificate_validation = True
    h2.add_credentials(self.options.username, self.options.password)

 
    # fetch the imageid
    tmpxml =  h2.request('http://' + self.options.server + '/api/v1/images/' + image_id)
    tmpdata = xobj.parse(tmpxml[1])

    #epdb.st()

    print "id: " + tmpdata.image.image_id
    print "name: " + tmpdata.image.name
    print "type: " + tmpdata.image.image_type.key
    print "timecreated: " + tmpdata.image.time_created
    print "trovename: " + tmpdata.image.trove_name
    print "trailingversion: " + tmpdata.image.trailing_version
    print "troveversion: " + tmpdata.image.trove_version 
    print "troveflavor: " + tmpdata.image.trove_flavor

    print "fileid: " + tmpdata.image.files.file.file_id
    print "filetitle: " + tmpdata.image.files.file.title
    print "fileurl: " + tmpdata.image.files.file.url

    #for file in tmpdata.images.files:
    #    epdb.st()
   

def help_image_build(self):
    print "image_build: build an image from the latest group in a PBS"
    print "usage: image_build projectshortname branchname stage"

def do_image_build(self, args):

    # define REST session 
    h2 = httplib2.Http("~/import_spf/.cache")
    h2.disable_ssl_certificate_validation = True
    h2.add_credentials(self.options.username, self.options.password)

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
    stage_label = stage_label + '-' + str(args[2])

    # very basic input validation
    if str(args[2]) == "devel":
        stagename = "Development"
    elif str(args[2]) == "qa":
        stagename = "QA"

    # fetch a list of build definitions for the branch
    build_names = __get_build_names(self, projectshortname, branchname)
    #epdb.st()

    # create appcreator session
    print "starting appcreator session: %s %s %s %s" %(proj_id, branch_id, rebuild, stage_label)
    sessiondata = self.proxy.startApplianceCreatorSession(proj_id, branch_id, 
                                                          rebuild, stage_label)

    # [False, ['session-tUUlDZ', {'isApplianceCreatorManaged': True}]]
    pcreator_session = sessiondata[1][0]

    print "starting imagebuild with appcreator"
    
    #epdb.st()
    # newBuildsFromProductDefinition
    #   branch_id, Stagename, False, ['VMware ESX (x86)'], 'test-centos6-automation2-1347312349.eng.rpath.com@rpath:test-centos6-automation2-1347312349-1.0-devel' 
    returndata = self.proxy.newBuildsFromProductDefinition(branch_id, stagename, False, build_names, stage_label)

    # newBuildsFromProductDefinition is going to return the imageID
    #       [False, [34]]
    imageid = returndata[1][0]
    #epdb.st()

    # http://poc3.fe.rpath.com/api/v1/images/34  image/status = 100 or 300
    # http://poc3.fe.rpath.com/api/v1/images/34  image/status_message = Creating VMware (R) ESX Image or 'Job Finished'

    # fetch image status

    __watch_image_build(self, imageid)


def __watch_image_build(self, imageid):
    
    # define REST session 
    h2 = httplib2.Http("~/import_spf/.cache")
    h2.disable_ssl_certificate_validation = True
    h2.add_credentials(self.options.username, self.options.password)

    tmpxml =  h2.request('http://' + self.options.server +
                        '/api/v1/images/' + str(imageid))

    image_data = xobj.parse(tmpxml[1]) 
    #epdb.st()
    image_status = image_data.image.status
    
    while int(image_status) != 300:
        tmpxml =  h2.request('http://' + self.options.server +
                            '/api/v1/images/' + str(imageid))
        image_data = xobj.parse(tmpxml[1])
        image_status = image_data.image.status
        print image_data.image.status_message 
        time.sleep(2)

    if int(image_status) == 300:
       print "image %s build completed" % imageid

def __get_build_names(self, projectshortname, branchname):

    # build_names, passed as list of imageDefinitions/imageDefinition/name
    #   if created with rpathcmd, will be 'rpathcmd_image_def'
    '''
    <?xml version='1.0' encoding='UTF-8'?>
    <imageDefinitions>
      <imageDefinition>
        <name>VMware ESX (x86)</name>
    '''

    # define REST session 
    h2 = httplib2.Http("~/import_spf/.cache")
    h2.disable_ssl_certificate_validation = True
    h2.add_credentials(self.options.username, self.options.password)
    
    #https://qa3.eng.rpath.com/api/products/test-centos6-automation2-1347312349/versions/1.0/imageDefinitions
    tmpxml =  h2.request('http://' + self.options.server +
                '/api/products/' + projectshortname +
                '/versions/' + branchname + '/imageDefinitions' )

    tmpdata = xobj.parse(tmpxml[1])
    resultcount = self.getXobjElementChildCount(tmpdata.imageDefinitions, 'imageDefinition')

    build_names = []
    if (resultcount == 0):
        print "no imagedefs found, exiting ..."
        sys.exit(1)
    elif(resultcount == 1):
        print "single imagedef found"
        print tmpdata.imageDefinitions.imageDefinition.name
        print tmpdata.imageDefinitions.imageDefinition.container.name
        print tmpdata.imageDefinitions.imageDefinition.architecture.name
        build_names.append(str(tmpdata.imageDefinitions.imageDefinition.name))
    elif (resultcount > 1):
        for imagedef in tmpdata.imageDefinitions.imageDefinition:
            print imagedef.name
            print imagedef.container.name
            print imagedef.architecture.name
            build_names.append(str(imagedef.name))

    return build_names
            
    



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

# Return the number of child nodes (useful for collection that can have 0|1|many
def getXobjElementChildCount(self, element, attributeName):
    if not hasattr(element, attributeName):
        return 0
    else:
        if isinstance(getattr(element, attributeName), list):
            return len(getattr(element, attributeName))
        else:
            return 1

def help_image_descriptor_deploy(self):
    print "image_descriptor_deploy: fetch the deployment descriptor for an image on a given target"
    print "usage: image_descriptor_descriptor imageid targetid" 

def do_image_descriptor_deploy(self, args):

    __get_descriptor(self, args, "deploy")

def help_image_descriptor_launch(self):
    print "image_descriptor_launch: fetch the launch descriptor for an image on a given target"
    print "usage: image_descriptor_launch imageid targetid" 

def do_image_descriptor_launch(self, args):

    __get_descriptor(self, args, "launch")


def __get_descriptor(self, args, desctype):

    # api/v1/targets/1/descriptors/launch/file/53

    #epdb.st()
    (args, options) = parse_arguments(args)
    imageid = args[0]
    targetid = args[1]

    #epdb.st()

    # define REST session 
    h2 = httplib2.Http("~/import_spf/.cache")
    h2.disable_ssl_certificate_validation = True
    h2.add_credentials(self.options.username, self.options.password)

    tmpxml =  h2.request('http://' + self.options.server +
                        '/api/v1/images/' + str(imageid))            
   
    tmpdata = xobj.parse(tmpxml[1])
   
    #epdb.st()  
    for action in tmpdata.image.actions.action:
        # descriptor.id
        #   api/v1/targets/1/descriptors/deploy/file/53'

        #print action.descriptor.id
        action_words = action.descriptor.id.split('/')

        #print "%s %s %s" %(action_words[6], action_words[8], action_words[10])
        #if (action_words[6] == targetid) and (action_words[8] == 'deploy'):
        if (action_words[6] == targetid) and (action_words[8] == desctype):
            print "#%s" % action.descriptor.id
            print "#match: %s %s %s" %(action_words[6], action_words[8], action_words[10])

            # get the raw descriptor data
            tmpxml = h2.request(action.descriptor.id)
            #print "-------RAW_DESCRIPTOR_DATA------"
            #print tmpxml[1]
            #print "-------RAW_DESCRIPTOR_DATA------"

            # make descriptor human readable
            descriptordata = xobj.parse(tmpxml[1])
            descriptordict = {  'imageid': int(imageid),
                                'fileid' : int(action_words[10]),
                                'targetid': int(targetid),
                                'descriptor_type': desctype } 
            #epdb.st()
            print ""
            print "## DESCRIPTOR INFO ##"
            print "# %s \"%s\"" % (descriptordata.descriptor.metadata.displayName,
                                descriptordata.descriptor.metadata.descriptions.desc)
            print ""
            for field in descriptordata.descriptor.dataFields.field:

                # figure out what this field is called
                try:
                    print "%s \"%s\", required: %s" % (field.name, 
                                                    field.descriptions.desc, 
                                                    field.required)

                    # convert from unicode to ascii
                    fname = field.name.encode('ascii','ignore')
                    fdesc = field.descriptions.desc.encode('ascii','ignore')
                    freq = field.required.encode('ascii','ignore')
                    # add info to dictionary
                    descriptordict[fdesc] = {}
                    descriptordict[fdesc]['tag'] = fname
                    descriptordict[fdesc]['required'] = bool(freq)
                    #epdb.st()
                except:
                    print "%s \"%s\", required: N/A" % (field.name, 
                                                    field.descriptions.desc)
                    # convert from unicode to ascii
                    fname = field.name.encode('ascii','ignore')
                    fdesc = field.descriptions.desc.encode('ascii','ignore')
                    # add info to dictionary
                    descriptordict[fdesc] = {}
                    descriptordict[fdesc]['tag'] = fname
                    descriptordict[fdesc]['required'] = False

                # check for a default value    
                try:
                    print "\t*%s == default" % field.default
                    descriptordict[fdesc]['default'] = field.default.encode('ascii','ignore')
                except:
                    descriptordict[fdesc]['default'] = "NULL"

                # iterate through possible values    
                descriptordict[fdesc]['values'] = []
                try:
                    #epdb.st()
                    descriptordict[fdesc]['values'] = []
                    if len(field.enumeratedType.describedValue) > 1:
                        #epdb.st()
                        for value in field.enumeratedType.describedValue:
                            print "\t%s,\"%s\"" % (value.key, value.descriptions.desc)

                            vkey = value.key.encode('ascii','ignore')
                            vdesc = value.descriptions.desc.encode('ascii','ignore')

                            descriptordict[fdesc]['values'].append({vdesc : vkey})
                    else:
                        #epdb.st()
                        print "\t%s,\"%s\"" % (field.enumeratedType.describedValue.key,
                                            field.enumeratedType.describedValue.descriptions.desc)

                        vkey = field.enumeratedType.describedValue.key.encode('ascii','ignore')
                        vdesc = field.enumeratedType.describedValue.descriptions.desc.encode('ascii','ignore')

                        descriptordict[fdesc]['values'].append({vdesc : vkey})
                except:
                    pass
                    #print "\tno enumerated types"

            print "## DESCRIPTOR INFO ##"
            #epdb.st()
            pprint(descriptordict)
            print ""

            # fetch the event type
            eventtypeid = __get_event_type_id_by_name(self, desctype)
            descriptordict['event_type'] = int(eventtypeid)


            FORMAT = '%Y%m%d%H%M%S'
            timestamp = datetime.now().strftime(FORMAT)
            ymlfile = desctype + '-descriptor-' + timestamp + '.yml'
            xmlfile = desctype + '-descriptor-' + timestamp + '.xml'

            f = open(ymlfile, "w")
            yaml.dump(descriptordict, f)
            f.close()

            f = open(xmlfile, "w")
            f.write(tmpxml[1])
            f.close()

def __get_event_type_id_by_name(self, name):

    # filter terms do not seem to work for event types
    #   so we are forced to string match manually

    # define REST session 
    h2 = httplib2.Http("~/import_spf/.cache")
    h2.disable_ssl_certificate_validation = True
    h2.add_credentials(self.options.username, self.options.password)

    tmpxml =  h2.request('http://' + self.options.server +
                        '/api/v1/inventory/event_types')

    tmpdata = xobj.parse(tmpxml[1])

    #epdb.st()
    etid = ""
    for et in tmpdata.event_types.event_type:
        if name == "launch" and et.name == "launch system on target":
            etid = int(et.job_type_id)
        if name == "deploy" and et.name == "deploy image on target":
            etid = int(et.job_type_id)
    return etid

def help_image_descriptor_run(self):
    print "image_descriptor_run: post a job with a descriptor yaml file"
    print "usage: image_descriptor_run <path.to.yml.file>"

def do_image_descriptor_run(self, args):

    h2 = httplib2.Http("~/.rpathcmd/.cache")
    h2.disable_ssl_certificate_validation = True
    h2.add_credentials(self.options.username, self.options.password)

    (args, options) = parse_arguments(args)

    #epdb.st()
    filename = args[0]

    f = open(filename)
    dataMap = yaml.load(f)
    f.close
    #epdb.st()
    '''
     'descriptor_type': 'launch',
     'event_type': 18,
     'fileid': 53,
     'imageid': 85,
     'targetid': 1}
    '''
    # basic validation of inputs 
    for item in dataMap:
        print item
        #epdb.st()
        try:
            #print "%s %s" % (item, dataMap[item]['required']) 
            if dataMap[item]['required'] == True:
                print "\t%s: required ==  %s" % (item, dataMap[item]['required']) 
            elif dataMap[item]['required'] == False:
                print "\t%s: required ==  %s" % (item, dataMap[item]['required'])
        except:
            pass
            #print "blah"
