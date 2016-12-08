#!/usr/bin/env python

# A simple program that continuously polls an Android device
# and screen-grabs screen in PNG format.

# Requires: PyGTK, `adb` in $PATH

from subprocess import Popen, PIPE
import gtk, gobject, threading, time
from PIL import Image
import numpy as np
import zlib

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

            # Here, I experimented with gzip compression settings, and I found 3 to be most optimal
            # in terms of framerate over USB.
            proc = Popen(["adb","shell","stty raw; screencap | gzip -c -3"], stdout=PIPE)

            # Perform blocking I/O
            gzdata = proc.communicate()[0]

            # Decompress the data stream
            raw = zlib.decompress(gzdata, 15 + 32)

            # If you want, you can use numpy to transform the data.
            # For example, below, I convert RGBA to BGRA.
            # See http://stackoverflow.com/questions/7906814/converting-pil-image-to-gtk-pixbuf

            # Load the raw image in, swap the channels around, and use the Image
            #im=Image.frombuffer('RGBA',(1280,800),raw,"raw","RGBA",0,1)
            #data=np.array(im)

            #red,green,blue,alpha=data.T
            #data=np.array([blue,green,red,alpha])
            #data=data.transpose()

            #pic=gtk.gdk.pixbuf_new_from_array(data,gtk.gdk.COLORSPACE_RGB,8)

            pic=gtk.gdk.pixbuf_new_from_data(raw,gtk.gdk.COLORSPACE_RGB,True,8,1280,800,1280*4)

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
