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
  done_file = directory.decode().strip() + '/done.txt'
  if os.path.isfile(done_file):
    done += 1

print("%i videos started, %i done" % (len(directories), done))
