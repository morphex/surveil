# Configuration of fswebcam, ffmpeg, etc
#


# Rotate images taken, 90, 180 or 270 degrees
#
# My webcam is upside-down, so I rotate it 180 degress (: :)
ROTATE = 180

# Length of generated video
VIDEO_MINUTES = 5

# Frames to skip before capturing image
#
# If surveil reports a lot of errors from fswebcam like this:
#
#   GD Error: gd-jpeg: JPEG library reports unrecoverable error: Unsupported
#   marker type 0x28Captured frame in 0.00 seconds.
#
# Try increasing the SKIP_FRAMES, up to 20
#
SKIP_FRAMES = 0

# Input selected, fswebcam -i argument
INPUT = "0"

# Seconds to sleep between each image
SLEEP_SECONDS = 10

# Format of time on images, run command "man strftime"
STRFTIME = "%Y-%m-%d %H:%M:%S (%Z)"

# Regarding RESOLUTION, DEADLINE and ENCODING_SPEED; a setup of
# 1280x720, realtime and 5 goes down comfortably on my 4-core
# demo board, with ARMv7 Processor rev 5 (v7l), 48.00 BogoMIPS
#
# It takes about 1 minute to encode a 2-minute video with 10
# SLEEP_SECONDS.
#
# And ffmpeg takes up about 256 MBs of RAM.

# Resolution of captured images, run command "v4l2-ctl --list-formats-ext|less"
#
# If command is missing, run "apt install v4l-utils"
#
# 1280x720 is large, 544x288 smaller and faster to encode using ffmpeg
# 432x240 640x480
RESOLUTION = "1280x720"

# The ffmpeg -deadline argument
#
# best, good or realtime, where realtime is fastest
DEADLINE = "realtime"

# -8 to 8, 8 is fastest
#
ENCODING_SPEED = 5

if int(RESOLUTION.split("x")[0]) >= 1280:
    # If resolution is higher than or equal to 1280, we can split up
    # the processing in 4 tiles, and 4 threads.
    TILE_COLUMNS = " -tile-columns 4 "
    THREADS = " -threads 4 "
elif int(RESOLUTION.split("x")[0]) >= 640:
    # If resolution is higher than or equal to 640, we can split up
    # the processing in 2 tiles, and 2 threads.
    TILE_COLUMNS = " -tile-columns 2 "
    THREADS = " -threads 2 "
else:
    TILE_COLUMNS = " "
    THREADS = " "
