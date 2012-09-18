rpathcmd
========

framework ported from https://fedorahosted.org/spacewalk/wiki/spacecmd

## Installing
* install httplib2 (yum install python-httplib2 / conary update httplib2=contrib.rpath.org@rpl:2-py26)
* install genshi (easy_install genshi / yum install python-genshi)
* cd /usr/lib/python2.6/site-packages
* hg clone http://hg.rpath.com/xobj
* hg clone http://hg.rpath.com/epdb
* git clone https://github.com/jctanner/rpathcmd.git
* ln -s /usr/lib/python2.6/site-packages/rpathcmd/rpathcmd /usr/bin/rpathcmd

## Configuring

1. mkdir ~/.rpathcmd
1. echo '[rpathcmd]' > ~/.rpathcmd/config
1. echo "username=\<username\>" >> ~/.rpathcmd/config
1. echo "password=\<password\>" >> ~/.rpathcmd/config
1. echo "server=\<rcehostname\>" >> ~/.rpathcmd/config


## Help

<pre>
[rba.admin@jtshell ~]$ rpathcmd help

Documented commands (type help <topic>):
========================================
api_v1_info             my_systems_list                 project_branches_list
api_versions            package_spfimport               project_create       
group_create            packages_list                   projects_list        
group_list              platforms_list                  system_group_update  
image_build             project_branch_create           system_info          
image_info              project_branch_imagedef_create  system_showconfig    
image_launchdescriptor  project_branch_imagedef_list    systems_list         
images_list             project_branch_stages_list      targets_list         

Undocumented commands:
======================
help
</pre>

## Example: simple project
<pre>
#!/bin/bash
PROJECT='jt-api-rpathcmd-01'
BRANCH='trunk'
PACKAGES='openssh-server,openssh-clients,strace'
FREESPACE='1024'
PLATFORM='centos6.rpath.com@rpath:centos-6e'
PLATFORMID=$(rpathcmd platforms_list | fgrep $PLATFORM | cut -d\: -f1)

rpathcmd project_create $PROJECT $PROJECT
rpathcmd project_branch_create $PROJECT $BRANCH $PLATFORMID $PLATFORM
rpathcmd project_branch_imagedef_create $PROJECT $BRANCH $FREESPACE
rpathcmd group_create $PROJECT $BRANCH $PACKAGES
rpathcmd image_build $PROJECT $BRANCH devel
</pre>

## Example: apache + configurator
<pre>
#!/bin/bash
PROJECT='webserver0007'
BRANCH='apache'
PACKAGES='openssh-server,openssh-clients,strace,httpd,httpd-configurator'
FREESPACE='1024'
PLATFORM='centos6.rpath.com@rpath:centos-6e'
PLATFORMID=$(rpathcmd platforms_list | fgrep $PLATFORM | cut -d\: -f1)
SPFURL='http://tannerjc.net/rpath/packages/linux/httpd-configurator/httpd-configurator-3.0.0.0.tar.gz'

rpathcmd project_create $PROJECT $PROJECT
rpathcmd project_branch_create $PROJECT $BRANCH $PLATFORMID $PLATFORM
rpathcmd project_branch_imagedef_create $PROJECT $BRANCH $FREESPACE
rpathcmd package_spfimport $PROJECT $BRANCH $SPFURL 
rpathcmd group_create $PROJECT $BRANCH $PACKAGES
rpathcmd image_build $PROJECT $BRANCH devel
</pre>
