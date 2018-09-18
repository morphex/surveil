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
SKIP_FRAMES = 10

# Input selected, fswebcam -i argument
INPUT = "0"
