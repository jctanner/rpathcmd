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
    
