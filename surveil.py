import os, time, subprocess, sys
import smtplib, imghdr

from email.message import EmailMessage

TMPFS_SIZE_MB = 50
TMPFS_SIZE = 1024 * 1024 * TMPFS_SIZE_MB

SURVEIL_DIR = 'surveil'

# Seconds to sleep between each picture taken
SLEEP_SECONDS = 10

DEVICE = '/dev/video0'

_CWD = os.getcwd()
_INDEX = 0

def test_dependencies():
    if subprocess.call(['fswebcam', '--help']) != 255:
        print('Missing fswebcam')
        print('Running "sudo apt install fswebcam"')
        os.system("apt install fswebcam")
    try:
        global DNS
        import DNS
    except ImportError:
        os.system("apt install python3-dns")
        global DNS
        import DNS

test_dependencies()

if len(sys.argv) != 2:
    print("Run as: ./%s %s" % (sys.argv[0], 'email@example.com'))
    sys.exit(1)

def start():
    os.system('mount -t tmpfs -o size=%s  none %s/surveil' % 
		(TMPFS_SIZE, _CWD))
    os.mkdir('%s/%s/images' % (_CWD, SURVEIL_DIR))
    os.chdir('%s/%s' % (_CWD, SURVEIL_DIR))

def exit():
    os.system('umount --force %s/%s' % (_CWD,SURVEIL_DIR))

start()

def message(filename):
    msg = EmailMessage()
    msg['Subject'] = 'Surveillance photos'
    msg['From'] = sys.argv[1]
    msg['To'] = sys.argv[1]
    msg.preamble = 'Surveillance photo attached'

    with open(filename, 'rb') as file:
        data = file.read()
    msg.add_attachment(data, maintype='image',
			subtype=imghdr.what(None, data))

    domain = sys.argv[1].split('@')[-1]
    for MX in DNS.mxlookup(domain):
        host = MX[1]
        try:
            connection = smtplib.SMTP(host)
            connection.send_message(msg)
            connection.close()
            print("Sent email")
            break
        except:
            pass


while 1:
    _time = time.time()
    filename = '%08i.jpg' % _INDEX
    path = 'images/%s' % filename
    os.system('fswebcam -d %s %s' % (DEVICE, path))
    message(path)
    while time.time() < (_time + SLEEP_SECONDS):
        time.sleep(0.5)
        print("Sleeping 0.5..")
    _INDEX += 1
exit()

