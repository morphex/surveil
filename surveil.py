import os, time, subprocess, sys
import smtplib, imghdr
import glob
import config
import traceback

from email.message import EmailMessage
import email.utils

startup_time = time.time()

TMPFS_SIZE_MB = 50
TMPFS_SIZE = 1024 * 1024 * TMPFS_SIZE_MB

# Percentage of temporary storage used, before videos are moved to
# permanent storage
TMPFS_THRESHOLD = 75

SURVEIL_DIR = 'surveil'

_CWD = os.getcwd()
_INDEX = 0
_INDEX_VIDEO = 0

# (60) is one minute of images, (60 * 10) is 10 minutes
VIDEO_IMAGES = (60 * config.VIDEO_MINUTES) / config.SLEEP_SECONDS

# 5 KBs minimum; corrupt images are small
MINIMUM_IMAGE_SIZE = 1024 * 5

def test_dependencies():
    try:
        subprocess.call(['fswebcam', '--help'])
    except FileNotFoundError:
        print('Missing fswebcam')
        print('Running "sudo apt install fswebcam"')
        os.system("sudo apt install fswebcam")
    try:
        subprocess.call(['ffmpeg', '-version'])
    except FileNotFoundError:
        print('Missing ffmpeg')
        print('Running "sudo apt install ffmpeg"')
        os.system("sudo apt install ffmpeg")

    try:
        global DNS
        import DNS
    except ImportError:
        print("Missing python3-dns")
        print('Running "sudo apt install python3-dns"')
        os.system("sudo apt install python3-dns")
        global DNS
        import DNS

test_dependencies()

smtp_host = ""
smtp_user = ""
smtp_password = ""

if len(sys.argv) != 5:
    print("Run as: ./%s %s %s %s %s" % (sys.argv[0], 'email@example.com', 'smtp.outgoing.example.com', 'smtp user', 'smtp password'))
    print("Use smtp.outgoing.example.com:587 for SMTP port 587, default is 25")
    sys.exit(1)

try:
    smtp_host, smtp_port = sys.argv[2].split(':')
except ValueError:
    smtp_host = sys.argv[2]
    smtp_port = 25
smtp_user = sys.argv[3]
smtp_password = sys.argv[4]

def message_subject(subject="Surveillance video, surveil started"):
    msg = EmailMessage()
    msg['Subject'] = 'Surveillance video, surveil started'
    msg['From'] = sys.argv[3]
    msg['To'] = sys.argv[1]
    msg['Date'] = email.utils.formatdate(time.time())

    domain = sys.argv[1].split('@')[-1]
    while 1:
        try:
            for MX in (('', smtp_host,),): # DNS.mxlookup(domain):
                host = MX[1]
                try:
                    connection = smtplib.SMTP()
                    connection.connect(host, port=smtp_port)
                    try:
                        connection.starttls()
                    except smtplib.SMTPNotSupportedError:
                        print("starttls not supported for ", MX)
                    except RuntimeError:
                        print("SSL/TLS is not available to Python")
                    except:
                        traceback.print_exc()
                    connection.login(smtp_user, smtp_password)
                    connection.send_message(msg)
                    connection.close()
                    print("Sent email")
                    return
                except:
                    traceback.print_exc()
                    time.sleep(15)
        except Exception:
            print("Error sending mail: ")
            print(sys.exc_info())
            time.sleep(15) # So we don't spam the system
    print('message sent')

def start():
    try:
        os.mkdir("%s/%s" % (_CWD, SURVEIL_DIR))
    except FileExistsError:
        os.rename("%s/%s" % (_CWD, SURVEIL_DIR),
                  "%s/%s.%s" % (_CWD, SURVEIL_DIR, str(startup_time)))
        os.mkdir("%s/%s" % (_CWD, SURVEIL_DIR))
    try:
        os.mkdir("%s/longterm" % _CWD)
    except FileExistsError:
        os.rename("%s/longterm" % _CWD,
                  "%s/longterm.%s" % (_CWD, str(startup_time)))
        os.mkdir("%s/longterm" % _CWD)
    message_subject(subject="Surveillance video, surveil started")
    if not config.DISABLE_TEMPORARY_STORAGE:
        os.system('mount -t tmpfs -o size=%s  none %s/surveil' % 
            (TMPFS_SIZE, _CWD))
    os.mkdir('%s/%s/images' % (_CWD, SURVEIL_DIR))
    os.chdir('%s/%s' % (_CWD, SURVEIL_DIR))

def exit():
    os.system('umount --force %s/%s' % (_CWD,SURVEIL_DIR))

start()

def message_video(directory):
    msg = EmailMessage()
    msg['Subject'] = config.SUBJECT
    msg['From'] = sys.argv[1]
    msg['To'] = sys.argv[1]
    msg.preamble = 'Surveillance video attached'
    msg['Date'] = email.utils.formatdate(time.time())

    with open(directory + '/out.webm', 'rb') as file:
        data = file.read()
    msg.add_attachment(data, maintype='video',
			subtype='webm', filename='out.webm')
    with open(directory + '/info.txt', 'rb') as file:
        data = file.read()
    msg.add_attachment(data, maintype='text',
			subtype='plain', filename='info.txt')
    with open(directory + '/out.log', 'rb') as file:
        data = file.read()
    msg.add_attachment(data, maintype='text',
			subtype='plain', filename='out.log.txt')
    with open(directory + '/out2.log', 'rb') as file:
        data = file.read()
    msg.add_attachment(data, maintype='text',
			subtype='plain', filename='out2.log.txt')

    domain = sys.argv[1].split('@')[-1]

    while 1:
        try:
            for MX in (('', smtp_host,),): # DNS.mxlookup(domain):
                host = MX[1]
                try:
                    connection = smtplib.SMTP()
                    connection.connect(host, port=smtp_port)
                    try:
                        connection.starttls()
                    except smtplib.SMTPNotSupportedError:
                        print("starttls not supported for ", MX)
                    except RuntimeError:
                        print("SSL/TLS is not available to Python")
                    except:
                        traceback.print_exc()
                    connection.login(smtp_user, smtp_password)
                    connection.send_message(msg)
                    connection.close()
                    os.system("rm %s/*" % directory)
                    print("Sent email")
                    return
                except:
                    traceback.print_exc()
                    time.sleep(15)
        except Exception:
            print("Error sending mail: ")
            print(sys.exc_info())
            time.sleep(15) # So we don't spam the system
    print('message sent')

def setup_video():
    valid_files = []
    for file in glob.glob('images/*.jpg'):
        if (os.path.getsize(file) > MINIMUM_IMAGE_SIZE) and imghdr.what(file) == 'jpeg':
            valid_files.append(file)
        else:
            os.unlink(file)
    if len(valid_files) >= VIDEO_IMAGES:
        valid_files.reverse()
        global _INDEX_VIDEO
        video_dir = 'video%06i' % _INDEX_VIDEO
        _INDEX_VIDEO += 1
        os.mkdir(video_dir)
        count = 1
        for file in valid_files:
            os.system("mv %s %s/%08i.jpg" % (file, video_dir, count))
            count += 1
        os.chdir(video_dir)
        script = open('run.sh', 'w')
        script.write("#!/bin/bash\n")
        script.write("time ffmpeg -framerate 1 -start_number 1 -i %08d.jpg ")
        script.write("-c:v libvpx-vp9 -deadline %s -cpu-used %i " %
            (config.DEADLINE, config.ENCODING_SPEED,))
        script.write(config.TILE_COLUMNS)
        script.write(config.THREADS)
        script.write("out.webm&>out.log\n")
        script.write("echo `date` > info.txt\n")
        script.write("echo %s >> info.txt\n" % startup_time)
        script.write("echo `uptime` >> info.txt\n")
        script.write("echo 1 > done.txt\n")
        script.close()
        os.system("chmod +x run.sh")
        os.system("./run.sh&>out2.log&")
        os.chdir(_CWD + '/' + SURVEIL_DIR)
        return True
    else:
        return False

def mailer():
    while 1:
        for video in glob.glob("video??????") +\
          glob.glob("../surveil.*.*/video??????"):
            try:
                os.stat(video + "/done.txt")
                message_video(video)
                break
            except FileNotFoundError:
                pass
        if config.REBOOT:
            if ((config.REBOOT * 60 * 60) + startup_time) < time.time():
                # FIXME, make sure no mail is unsent
                os.system("/sbin/reboot")
        time.sleep(5) # So we don't spam the system

# Start mailer
import _thread
_thread.start_new_thread(mailer, ())

# Main loop
while 1:
    _time = time.time()
    filename = '%08i.jpg' % _INDEX
    path = 'images/%s' % filename
    while 2:
        process = subprocess.Popen(['fswebcam', '-S', str(config.SKIP_FRAMES),
                                '--jpeg', str(95),
                                '--rotate', str(config.ROTATE),
				'-d', config.DEVICE,
                                '-i', config.INPUT,
                                '--timestamp', config.STRFTIME,
                                '-r', config.RESOLUTION,
                                path], stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        #print(process)
        process.wait()
        output = process.stderr.read() + process.stdout.read()
        output = str(output)
        #print(type(output))
        #print((output,))
        if output.lower().find('error') > -1:
            print("fswebcam reported error: ")
            print(output)
            # So we don't spam the system with repeated requests
            time.sleep(1)
        else:
            break
    #message(path)
    setup_video()
    while time.time() < (_time + config.SLEEP_SECONDS):
        time.sleep(0.5)
        #print("Sleeping 0.5..")
    _INDEX += 1
exit()

