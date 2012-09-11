rpathcmd
========

framework ported from https://fedorahosted.org/spacewalk/wiki/spacecmd

## Installing
1. cd /usr/lib/python2.6/site-packages
2. hg clone http://hg.rpath.com/xobj
3. hg clone http://hg.rpath.com/epdb
4. git clone https://github.com/jctanner/rpathcmd.git
5. ln -s /usr/lib/python2.6/site-packages/rpathcmd/rpathcmd /usr/bin/rpathcmd

## Configuring

1. mkdir ~/.rpathcmd
2. echo '[rpathcmd]' > ~/.rpathcmd/config
3. echo "username=<username>" >> ~/.rpathcmd/config
4. echo "password=<password>" >> ~/.rpathcmd/config
5. echo "server=<rcehostname>" >> ~/.rpathcmd/config

