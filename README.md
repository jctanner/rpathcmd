rpathcmd
========

framework ported from https://fedorahosted.org/spacewalk/wiki/spacecmd

## Installing
1. install httplib2
* yum install python-httplib2
* conary update httplib2=contrib.rpath.org@rpl:2-py26
1. cd /usr/lib/python2.6/site-packages
1. hg clone http://hg.rpath.com/xobj
1. hg clone http://hg.rpath.com/epdb
1. git clone https://github.com/jctanner/rpathcmd.git
1. ln -s /usr/lib/python2.6/site-packages/rpathcmd/rpathcmd /usr/bin/rpathcmd

## Configuring

1. mkdir ~/.rpathcmd
1. echo '[rpathcmd]' > ~/.rpathcmd/config
1. echo "username=\<username\>" >> ~/.rpathcmd/config
1. echo "password=\<password\>" >> ~/.rpathcmd/config
1. echo "server=\<rcehostname\>" >> ~/.rpathcmd/config

