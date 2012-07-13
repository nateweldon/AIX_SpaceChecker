#!/usr/bin/python

import sys, cmd, os, re, logging, csv, getopt
from datetime import datetime
from paramiko import SSHClient, SSHConfig, AutoAddPolicy
from mailer import mailer
from config import *

def setupLogger(name):
	logger = logging.getLogger(name)
	logger.setLevel(logging.DEBUG)
	FORMAT = '%Y%m%d%H%M%S'
	timestamp = datetime.now().strftime(FORMAT)
	hdlr = logging.FileHandler(LOGDIR + "/" + name + "_" + timestamp + '.log')
	formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
	hdlr.setFormatter(formatter)
	logger.addHandler(hdlr)
	return logger
 

def get_sshConfig():
	sshConfig = SSHConfig()
	sshConfig.parse(open(HOME_SSH_CONFIG))
	return sshConfig	

def get_sshClient():
	client = SSHClient()
	client.set_missing_host_key_policy(AutoAddPolicy())
	client.load_system_host_keys()
	return client

def stripStupidWindowsInfo(serverInfo):
	hostname = serverInfo['hostname']
	hostname = hostname.rstrip()
	idfile = serverInfo['identityfile']
	idfile = idfile.rstrip()
	idfile = re.sub("~", HOME, idfile)
	user = serverInfo['user']	
	user = user.rstrip()
	serverInfo['hostname'] = hostname
	serverInfo['user'] = user
	serverInfo['identityfile'] = idfile
	return serverInfo


def logInformation(client, logger, cmd, name):
	print " ++++++++++++++++++++++++++++++++++++" + name + "++++++++++++++++++++++++++++++++++++++++++++"
	logger.debug(" ++++++++++++++++++++++++++++++++++++" + name + "++++++++++++++++++++++++++++++++++++++++++++" )
	for command in cmd:
		stdin, stdout, stderr = client.exec_command(command)
		for i, line, in enumerate(stdout):
			line = line.rstrip()
			if 'tempfs' not in line:
				print "%d: %s" % (i, line)
				logger.debug("%d: %s" % (i, line))
		print "\n"
		logger.debug("\n")

def spaceCheck(client, logger, cmd, name):
	space_warning = 0
	stdin, stdout, stderr = client.exec_command(cmd)
	for i, line, in enumerate(stdout):
		line = line.rstrip()
		if 'tempfs' not in line:
			info = line.split(' ')
			space = info[1].split("%")
			if (space[0].isdigit() and int(space[0]) >= 90 ):
				space_warning = 1
				logger.debug("Warning " + info[0] + " on " + name + " is at " + info[1] + " Mounted on " + info[2])
	return space_warning

def find_most_recent(directory, partial_file_name):
   # list all the files in the directory
    files = os.listdir(directory)
    # remove all file names that don't match partial_file_name string
    files = filter(lambda x: x.find(partial_file_name) > -1, files)
    directory = directory + "/"
    # create a dict that contains list of files and their modification timestamps
    name_n_timestamp = dict([(x, os.stat(directory+x).st_mtime) for x in files])
    # return the file with the latest timestamp
    return max(name_n_timestamp, key=lambda k: name_n_timestamp.get(k))	


def main(argv):
	try:
		opts, args = getopt.getopt(argv, "h:i")
	except getopt.GetoptError:
		print 'checkDiskSpace.py or checkDiskSpace.py -h'
		sys.exit(2)
	for opt, arg in opts: 
		if opt == '-h':
			print ' Nate Add help documentation'
			sys.exit()
		elif opt == '-i':
			print 'interactive mode'
			
			ssh_Config = get_sshConfig()
			ssh_Client = get_sshClient()
			aix_logger = setupLogger('AIX_LOGGER')
			aix_errors = setupLogger('AIX_ERRORS')
			email_check = 0
			for server in SERVER_LIST:
				serverName = ssh_Config.lookup(server)
				serverName = stripStupidWindowsInfo(serverName)
				print " serverName" + serverName['hostname'] + " user " + serverName['user'] + " Key" + serverName['identityfile']
 				ssh_Client.connect(serverName['hostname'], username=serverName['user'], password=sshPassword, key_filename=serverName['identityfile'])
				check_cmd = " df | sed '1d' | awk '{print $1 ',' $4 ',' $7}' " #| cut -d'%' -f1"
				cmd = " df "
				logCmd = [cmd, 'iostat']
				logInformation(ssh_Client, aix_logger, logCmd, serverName['hostname'])
				#logInformation(ssh_Client, aix_logger, 'iostat', serverName['hostname'])
				email_check += spaceCheck(ssh_Client, aix_errors, check_cmd, serverName['hostname'])
			if (email_check > 0):
				print "sending error email"
				aixlog = find_most_recent(LOGDIR, 'AIX_LOGGER')
				aixerror = find_most_recent(LOGDIR, 'AIX_ERRORS')
				logs = [LOGDIR + "/" + aixlog, LOGDIR + "/" + aixerror]
				#mailer.mail(errorUser, errorSubject, errormailText, logs, gmailUser, gmailPwd)
			else:
				print "sending ok email"
				aixlog = find_most_recent(LOGDIR, 'AIX_LOGGER')
				logs = [LOGDIR + "/" + aixlog]
				mailer.mail(okUser, okSubject, okmailText, logs, gmailUser, gmailPwd)


if __name__ == '__main__':
	main(sys.argv[1:])
