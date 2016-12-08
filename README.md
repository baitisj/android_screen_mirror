# android_screen_mirror
Scripts to perform screen capture of Android devices

**3+ FPS possible!**

View the source of the python script to see the requirements and
to enact changes that may make it work better on your platform!

## Requiremens

Android device requirements:
   * adb (Android device bridge) debug mode ENABLED
   * (probably) should probably have [stericson's BusyBox](https://play.google.com/store/apps/details?id=stericson.busybox) installed.

Computer (host) requirements:
   * `adb`
   * `python` (version 2) 
   * `pygtk`

## About the variations

There are a few variants of this program.
All versions use the Android `screencap` command to get data.
Scripts that do NOT include the word `raw` are more likely to
be compatible with all hardware; they use PNG images as 
transport. However, PNG compression adds overhead. Which is why
I developed the `raw` versions.

# The fastest version!

The fastest performer (for me and my hardware) is:

   `android_screen_mirror_raw_network.py`

Right now, this script does NOT account for screen rotation, and
it assumes that your display is 32-bit per pixel RGBA (which is
probably a pretty good assumption for most hardware).

I can easily get 3+ fps using this method which, in my opinion,
is more than adequate for screen grabs.
