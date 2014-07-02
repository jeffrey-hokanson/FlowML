#! /usr/bin/python
# 
try:
    f = open('password.sha1')
    password = f.readline()
    f.close()
    if password[0:4] != u'sha1':
        raise ValueError('password file not in valid format')
except:
    print "Please enter a password for this notebook."
    print "The resulting SHA1 will be saved in password.sha1 for future use"
    from IPython.lib import passwd
    password = passwd() 
    c.NotebookApp.password = password
    f = open('password.sha1','w')
    f.write(password)
    f.close()
