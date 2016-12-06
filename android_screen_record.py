#!/usr/bin/env python

# TODO
# This program will use FFMPEG
# 

#Writing
#
# To write a series of frames of size 460x360 into the file
# 'my_output_videofile.mp4', we open FFMPEG and indicate that raw RGB data is
# going to be piped in:
#
#command = [ FFMPEG_BIN,
#        '-y', # (optional) overwrite output file if it exists
#        '-f', 'rawvideo',
#        '-vcodec','rawvideo',
#        '-s', '420x360', # size of one frame
#        '-pix_fmt', 'rgb24',
#        '-r', '24', # frames per second
#        '-i', '-', # The imput comes from a pipe
#        '-an', # Tells FFMPEG not to expect any audio
#        '-vcodec', 'mpeg'",
#        'my_output_videofile.mp4' ]
#
# pipe = sp.Popen( command, stdin=sp.PIPE, stderr=sp.PIPE)
#
# The codec of the output video can be any valid FFMPEG codec but for many
# codecs you will need to provide the bitrate as an additional argument (for
# instance -bitrate 3000k). Now we can write raw frames one after another
# in the file. These will be raw frames, like the ones outputed by FFMPEG in the
# previous section: they should be strings of the form “RGBRGBRGB…” where R,G,B
# are caracters that represent a number between 0 and 255. If our frame is
# represented as a Numpy array, we simply write:
# 
# pipe.proc.stdin.write( image_array.tostring() )


# A simple program that continuously polls an Android device
# and screen-grabs screen in PNG format.

# Requires: PyGTK, `adb` in $PATH

from subprocess import Popen, PIPE
import gtk, gobject, threading, time

class MainWindow(gtk.Window):

    def __init__(self):
        super(MainWindow,self).__init__()
        self.img=gtk.Image()
        self.add(self.img)

        self.stopthread = threading.Event()
        threading.Thread(target=self.pull_data).start()

    ## Thread continously pulls image data over adb from the device.
    def pull_data(self):
        self.last_time=time.time()
        while not self.stopthread.isSet():

            # Ideally, your adb tools would support `adb exec-out`
            # However, mine does not
            # If `adb exec-out` works on your platform, change the following command to:
            # proc = Popen(["adb","exec-out","screencap -p"], stdout=PIPE)

            # Another potential issue: your device may not support 'stty raw'
            # You should try running this command manually in an interactive shell
            # to see if it will work.

            # `stty` is probably not included on Android devices; however --
            # Stericson's BusyBox installer for Android will install this; see
            # https://play.google.com/store/apps/details?id=stericson.busybox
            #
            # As of this writing, I do NOT recommend JRummy's busybox as it seems
            # to be buggy.

            proc = Popen(["adb","shell","stty raw; screencap -p"], stdout=PIPE)

            # Perform blocking I/O
            png = proc.communicate()[0]

            # Load the PNG image into gdk and obtain a decompressed pixbuf
            loader=gtk.gdk.PixbufLoader()
            loader.write(png)
            loader.close()
            pic=loader.get_pixbuf()
            self.img.set_from_pixbuf(pic)

            # Some helpful framerate statistics
            self.current_time=time.time()
            print ("{:10.2f} fps\r".format(1.0/(self.current_time - self.last_time))),
            self.last_time = self.current_time

            # Displays windows if they're not already showing
            self.show_all()

    def stop(self):
        self.stopthread.set()


def main_quit(obj):
    global win
    win.stop()
    gtk.main_quit()

def main():
    gtk.gdk.threads_init()
    global win
    win = MainWindow()

    # If we close the main window, this causes the image sucking thread to stop
    win.connect("destroy",main_quit)

    gtk.main()

# Run our main function if we're in the default scope
if __name__ == "__main__":
    main()
