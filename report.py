import os
import config
import subprocess

_CWD = os.getcwd()

process = subprocess.Popen("./report.sh", stdout=subprocess.PIPE,
		stderr=subprocess.PIPE)
process.wait()
directories = process.stdout.readlines()
done = 0
for directory in directories:
  directory_ = directory.decode().strip() + '/done.txt'
  print(directory_)
  if os.path.isfile(directory_):
    done += 1

print("%i videos started, %i done" % (len(directories), done))
