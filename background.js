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
		port.onMessage.addListener(onNativeAppMessage);
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
	var querying = browser.tabs.query({highlighted: true, currentWindow: true});
	querying.then(processTabs, onTabQueryError);
}

function processTabs(tabs) {
	connectNative();
	var title;
	var msg;
	var notificationTimeout = 3000;
	if (tabs.length == 1) {
		title = clickedTab.title;
		msg = 1 + "\n"
			+ clickedTab.title + "\n"
			+ clickedTab.url
	} else {
		title = tabs.length + " videos";
		msg = tabs.length + "\n"
			+ title + "\n";
		for (let tab of tabs) {
			msg = msg
				+ tab.url + "\n";
		}
	}
	console.log("yt-dl-ext: Sending to native app: " + title);
	port.postMessage(msg);
	createNotification("yt-dl-ext: Download starting", title, notificationTimeout);
}

function onTabQueryError(error) {
	console.log("yt-dl-ext: Error getting list of selected tabs: " + error);
}

function onNativeAppMessage(response) {
	if ( response.substring(0,2) != '^%' ) {
		console.log("yt-dl-ext: Native app said: " + response);
		return;
	}
	response = response.substring(2);
	switch (true) {
		case /^Finished downloading /.test(response):
			var title = response.substring("Finished downloading ".length);
			createNotification("yt-dl-ext: Download finished", title, 7000);
			break;
		default:
			console.log("yt-dl-ext: ERROR: unknown message from native app");
			break;
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


