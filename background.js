browser.contextMenus.create({
	id: "yt-dl-ext_download",
	title: "Download with yt-dl-ext",
	contexts: ["tab"]
});

browser.contextMenus.onClicked.addListener(contextMenuAction);

var port;

function connectNative() {
	port = browser.runtime.connectNative("yt_dl_ext");
	port.onMessage.addListener((response) => {
	  console.log("yt-dl-ext: Received from native app: " + response);
	});
	port.onDisconnect.addListener((p) => {
	  console.log("yt-dl-ext: Disconnected from native app with error: " + p.error);
	});
}

function contextMenuAction(info, tab) {
	connectNative();
	
	console.log("yt-dl-ext: Sending to native app: " + tab.url);
	port.postMessage(tab.url);
}

