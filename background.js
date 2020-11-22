browser.contextMenus.create({
	id: "yt-dl-ext_download",
	title: "Download with yt-dl-ext",
	contexts: ["tab"]
});

browser.contextMenus.onClicked.addListener(contextMenuAction);

var port = null;
var clickedTab;

function connectNative() {
	if ( port == null ) {
		port = browser.runtime.connectNative("yt_dl_ext");
		port.onMessage.addListener((response) => {
			console.log("yt-dl-ext: Native app said: " + response);
		});
		port.onDisconnect.addListener((p) => {
			if ( p.error ) {
				console.log("yt-dl-ext: Disconnected from native app with error: " + p.error);
			} else {
				console.log("yt-dl-ext: Disconnected from native app");
			}
			port = null;
		});
	}
}

function contextMenuAction(info, tab) {
	clickedTab = tab;
	querying = browser.tabs.query({highlighted: true, currentWindow: true});
	querying.then(processTabs, onTabQueryError);
}

function processTabs(tabs) {
	connectNative();
	if (tabs.length == 1) {
		console.log("yt-dl-ext: Sending to native app: " + clickedTab.url);
		port.postMessage(clickedTab.url);
		notifyStartDownload(1, clickedTab.title);
	} else {
		for (let tab of tabs) {
			console.log("yt-dl-ext: Sending to native app: " + tab.url);
			port.postMessage(tab.url);
		}
		notifyStartDownload(tabs.length, null);
	}
}

function onTabQueryError(error) {
	console.log("yt-dl-ext: Error getting list of selected tabs: " + error);
}

function notifyStartDownload(count, title) {
	var timeout = 3000;
	if ( count == 1 ) {
		createNotification("yt-dl-ext: Download starting", title, timeout);
	} else {
		createNotification("yt-dl-ext: Download starting", "Downloading " + count + " videos", timeout);
	}
}

function createNotification(title, message, timeout) {
	browser.notifications.create({
		"type": "basic",
		"iconUrl": null,
		"title": title,
		"message": message
	}).then( (notificationId) =>
		setTimeout(() => browser.notifications.clear(notificationId), timeout) );
}


