rpathcmd
========

framework ported from https://fedorahosted.org/spacewalk/wiki/spacecmd

## Installing
* install httplib2 (yum install python-httplib2 / conary update httplib2=contrib.rpath.org@rpl:2-py26)
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
[poc3.jtanner@jtshell ~]$ rpathcmd help

Documented commands (type help <topic>):
========================================
api_v1_info   platforms_list                  projects_list      
api_versions  project_branch_create           system_group_update
group_create  project_branch_imagedef_create  system_info        
group_list    project_branch_stages_list      systems_list       
image_info    project_branches_list         
images_list   project_create                

Undocumented commands:
======================
help
</pre>

## Example
<pre>
NEWPROJ='jt-api-rpathcmd-01'
NEWBRANCH='trunk'
PACKAGES='openssh-server,openssh-clients,strace'
PLATFORM='centos6.rpath.com@rpath:centos-6e'
PLATFORMID=$(rpathcmd platforms_list | fgrep $PLATFORM | cut -d\: -f1)

rpathcmd project_create $PROJECT $PROJECT
project_branch_create $PROJECT $BRANCH $PLATFORMID $PLATFORM
rpathcmd group_create $PROJECT $BRANCH $PACKAGES
rpathcmd image_build $PROJECT $BRANCH devel
</pre>
