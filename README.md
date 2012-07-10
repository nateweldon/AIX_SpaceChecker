AIX_SpaceChecker
================

Script to use paramiko to ssh to a bunch of unix servers and check the space

you will need to install paramiko and then you need a config file named config.py

containing the following 

HOME_SSH_CONFIG = "" / home ssh config file
HOME =  "" // home directory location
SERVER_LIST =  "" // server list
LOGDIR =  "" // log directory


gmail_user = "" // gmail user to send email
gmail_pwd =  "" // password

to_user =  "" // who the email gets sent to

mailText = """

Thanks, 

Your friendly neighborhood AIX Space Daemon"""

subject= "" // subject of email
