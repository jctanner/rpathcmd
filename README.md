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

