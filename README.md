## School project for the course SMAP (Smart approaches to creating IS and applications) at the University of Hradec Králové

A Mozilla Firefox browser extension for easy youtube video downloading with only 2 mouse clicks. Using `youtube-dl` for downloading, it is simple and user friendly - no need to use command line.

Makes possible to download video of the currently opened page, or any video from any link that can be seen on the page. Also possible to download multiple tabs at once by selecting them. Download starts by right clicking and choosing the extension's item from context menu.

Extension's settings page allows to set additional command-line parameters for youtube-dl such as audio-only download, limit download bandwidth etc.

Demonstration video: https://youtu.be/o3A6s_y9p10

A IPython Notebook with neural network for video classification is also included. It classifies the videos based on their names and divides them into three categories: video, music, podcast. With a bit more programming it would be possible to run it on a remote server and connect it with the extension and then you could set command-line parameters that apply for each category, so that for example videos from 'podcast' category could be downloaded as audio-only etc.

### How to run the extension

If I were to continue working on this project, the next step would be making an installation script and publishing the extension in the Mozilla addons store, to make the installation easier. Without it, it's quite long:

1. Install python and then run this command to install necessary packages: `pip install requests gdown pyunpack`.

2. In `native-app/native_manifest.json` on line 4, change the path to the `yt-dl-ext_win.bat` file accordingly.

3. In `native-app/yt-dl-ext_win.bat` on line 3, change the path to the `yt-dl-ext.py` file accordingly.

4. Add registry keys
```
HKEY_CURRENT_USER\Software\Mozilla\NativeMessagingHosts\yt_dl_ext
HKEY_LOCAL_MACHINE\Software\Mozilla\NativeMessagingHosts\yt_dl_ext
``` 
- and for both the default key value must be path to the application manifest (e.g. `C:\Users\username\Documents\yt-dl-ext\native-app\native_manifest.json`).

5. Add the extension to the browser by going to `about:debugging#/runtime/this-firefox` clicking "Load temporary extension" and selecting our `manifest.json` in the file browser.
