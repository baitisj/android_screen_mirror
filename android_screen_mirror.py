#!/usr/bin/env python

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
