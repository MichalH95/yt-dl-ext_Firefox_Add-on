browser.contextMenus.create({
	id: "yt-dl-ext_download",
	title: "Download with yt-dl-ext",
	contexts: ["tab"]
});

browser.contextMenus.onClicked.addListener(contextMenuAction);

var port;
var clickedTab;

function connectNative() {
	port = browser.runtime.connectNative("yt_dl_ext");
	port.onMessage.addListener((response) => {
	  console.log("yt-dl-ext: Native app said: " + response);
	});
	port.onDisconnect.addListener((p) => {
	  console.log("yt-dl-ext: Disconnected from native app, error: " + p.error);
	});
}

function contextMenuAction(info, tab) {
	clickedTab = tab;
	querying = browser.tabs.query({highlighted: true, currentWindow: true});
	querying.then(processTabs, onError);
}

function processTabs(tabs) {
	connectNative();
	if (tabs.length == 1) {
		console.log("yt-dl-ext: Sending to native app: " + clickedTab.url);
		port.postMessage(clickedTab.url);
	} else {
		for (let tab of tabs) {
			console.log("yt-dl-ext: Sending to native app: " + tab.url);
			port.postMessage(tab.url);
		}
	}
}

function onError(error) {
	console.log("yt-dl-ext: Error getting list of selected tabs: " + error);
}

