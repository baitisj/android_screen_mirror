#!/usr/bin/env python

# A simple program that continuously polls an Android device
# and screen-grabs screen in PNG format.

# Requires: PyGTK, `adb` in $PATH

from subprocess import Popen, PIPE
import gtk, gobject, threading, time, socket
from contextlib import closing
import zlib
import signal

class MainWindow(gtk.Window):

    def __init__(self):
        super(MainWindow,self).__init__()
        self.img=gtk.Image()
        self.add(self.img)

        self.stopthread = threading.Event()
        self.ip = self.get_ip()
        self.display_width,self.display_height = self.get_resolution()
        print ("Device network IP is " + str(self.ip))
        threading.Thread(target=self.launch_screenshot_server).start()
        threading.Thread(target=self.pull_data).start()

    def get_resolution(self):
        proc = Popen(["adb","shell","wm size"], stdout=PIPE)
        result = proc.communicate()[0]
        fields = result.split()
        if len(fields) > 1:
            (width,height) = fields[2].split("x")
            return (int(width),int(height))
        return None

    def get_ip(self):
        proc = Popen(["adb","shell","ip route"], stdout=PIPE)
        # Scan output line by line and break into fields.
        # We are looking for something like this:
        # 192.168.X.X/24 dev wlan0  proto kernel  scope link  src 192.168.X.115  metric 307
        # 1              2   3      4     5       6     7     8   9              10     11
        # Field 9 therefore contains our IP address
        while True:
            out = proc.stdout.readline()
            if out != '':
                fields = out.split()
                if len(fields) >= 9:
                    return fields[8]
            else:
                break
        proc.kill()

    ## Thread that opens ADB and uses busybox netcat to screencap 
    ## every time a connection is made
    def launch_screenshot_server(self):
        # First, let's create a script in /mnt/asec (which is mounted tempfs) and make it executable
        temp = Popen(["adb","shell","echo '/system/bin/screencap | /system/bin/gzip -c -2' > /mnt/asec/fastcap.sh; chmod 700 /mnt/asec/fastcap.sh"],stdout=PIPE)
        status = temp.communicate()[0]
        # Next, launch the screenshot server. Retain handle for cleanup.
        self.screenshot_server = Popen(["adb","shell","nc -ll -p 8008 -e /system/bin/sh -c /mnt/asec/fastcap.sh"], stdout=PIPE)
        status = self.screenshot_server.communicate()[0]

    ## Cleans up the script that we've put in /mnt/asec
    def cleanup_script(self):
        temp = Popen(["adb","shell","rm /mnt/asec/fastcap.sh"],stdout=PIPE)
        status = temp.communicate()[0]

    def fetch_screenshot(self):
       s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
       try:
           s.connect((self.ip, 8008))
       except socket.error as msg:
           s.close()
           return None
       f=s.makefile('rb',bufsize=0)
       png=f.read()
       s.shutdown(socket.SHUT_WR)
       return png

    ## Thread continously pulls image data over the network.
    def pull_data(self):
        # Try to connect a max of 10 times to the server before giving up.
        # Once we connect, we keep going until something stops working.

        print "Starting screen capture"
        self.last_time=time.time()
        rt=0


        while not self.stopthread.isSet():
            gzdata=self.fetch_screenshot()
            if gzdata == None:
                # Retry while 
                print "Network connection failed. Retry #"+str(rt)
                rt = rt + 1
                time.sleep(1)
                continue

            # Check again to make sure our thread is ok
            # The transfer takes a lot of time
            if self.stopthread.isSet(): return
            # Load the PNG image into gdk and obtain a decompressed pixbuf
            raw = zlib.decompress(gzdata, 15 + 32)
            # NOTE: This may not be the correct bitdepth for your device, but somehow I doubt it...
            pic=gtk.gdk.pixbuf_new_from_data(raw,gtk.gdk.COLORSPACE_RGB,True,8,self.display_width,self.display_height,self.display_width*4)
            self.img.set_from_pixbuf(pic)

            # Some helpful framerate statistics
            self.current_time=time.time()
            print ("{:10.2f} fps\r".format(1.0/(self.current_time - self.last_time)))
            self.last_time = self.current_time

            # Displays windows if they're not already showing
            self.show_all()

    def stop(self):
        self.stopthread.set()
        self.screenshot_server.kill()
        self.cleanup_script()

def main_quit(obj):
    global win
    win.stop()
    gtk.main_quit()

def signal_handler(signal, frame):
    print('Goodbye, cruel world.')
    main_quit(frame)

def main():
    gtk.gdk.threads_init()
    global win
    win = MainWindow()

    signal.signal(signal.SIGINT, signal_handler)
    # If we close the main window, this causes the image sucking thread to stop
    win.connect("destroy",main_quit)
    gtk.main()

# Run our main function if we're in the default scope
if __name__ == "__main__":
    main()
