browser.contextMenus.create({
	id: "yt-dl-ext_download",
	title: "Download with yt-dl-ext",
	contexts: ["tab", "link"]
});

browser.contextMenus.onClicked.addListener(contextMenuAction);

function contextMenuAction(info, tab) {
	if ( info.linkUrl ) {  // link context menu
		processLink(info.linkUrl);
	} else {  // tab context menu
		clickedTab = tab;
		var querying = browser.tabs.query({highlighted: true, currentWindow: true});
		querying.then(processTabs, onTabQueryError);
	}
}


var port = null;
var clickedTab;
var startDlNotificationTimeout = 3000;
var debug = true;

function connectNative() {
	if ( port == null ) {
		port = browser.runtime.connectNative("yt_dl_ext");
		port.onMessage.addListener(onNativeAppMessage);
		port.onDisconnect.addListener(onNativeAppDisconnect);
	}
}

function onNativeAppDisconnect(p) {
	var title = "Disconnected from native app";
	var msg;
	if ( p.error ) {
		console.log("yt-dl-ext: Disconnected from native app with error: " + p.error);
		msg = "Error: " + p.error;
	} else {
		console.log("yt-dl-ext: Disconnected from native app");
		msg = "No errors";
	}
	if ( debug ) {
		createNotification(title, msg, 0);
	}
	port = null;
}

function processTabs(tabs) {
	connectNative();
	var title;
	var msg;
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
	createNotification("yt-dl-ext: Download starting", title, startDlNotificationTimeout);
}

function processLink(link) {
	connectNative();
	var msg = 1 + "\n"
		+ link + "\n"
		+ link;
	console.log("yt-dl-ext: Sending to native app: " + link);
	port.postMessage(msg);
	createNotification("yt-dl-ext: Download starting", link, startDlNotificationTimeout);
}

function onTabQueryError(error) {
	console.log("yt-dl-ext: Error getting list of selected tabs: " + error);
}

function onNativeAppMessage(response) {
	// special messages begin with ^%
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
		case /^Failed downloading /.test(response):
			var title = response.substring("Failed downloading ".length);
			createNotification("yt-dl-ext: Failed downloading", "Failed: " + title, 8000);
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
	}).then( (notificationId) => {
			if ( timeout > 0 ) {
				setTimeout(() => browser.notifications.clear(notificationId), timeout)
			}
		} );
}


