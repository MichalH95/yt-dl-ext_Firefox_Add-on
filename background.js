browser.contextMenus.create({
	id: "yt-dl-ext_download",
	title: "Download with yt-dl-ext",
	contexts: ["tab", "link"]
});

// browser.storage.onChanged.addListener(processStorageChange);

browser.contextMenus.onClicked.addListener(contextMenuAction);

function contextMenuAction(info, tab) {
	resendStorageToNativeApp();
	if ( info.linkUrl ) {  // link context menu
		processLink(info.linkUrl);
	} else {  // tab context menu
		clickedTab = tab;
		var querying = browser.tabs.query({highlighted: true, currentWindow: true});
		querying.then(processTabs);
	}
}


var port = null;
var clickedTab;
var startDlNotificationTimeout = 3000;
var debug = true;
var notificationPrefix = "yt-dl-ext: ";

function resendStorageToNativeApp() {
	var gettingItem = browser.storage.sync.get(['video', 'music', 'podcast', 'global']);
	gettingItem.then((results) => {
		connectNative();
		console.log(getConsoleLogPrefix() + "Sending extra command-line arguments to native app");

		var msg = "^%Extra command-line arguments change" + "\n";

		var changedItems = Object.keys(results);

		for (let item of changedItems) {
			msg = msg + item + "\n"
				  + results[item] + "\n";
		}
		port.postMessage(msg);
	});
}

function getConsoleLogPrefix() {
	var dt = new Date();
	var datetime = dt.getFullYear() + "-" + 
                + twoDigit(dt.getMonth()+1) + "-"
		+ twoDigit(dt.getDate()) + " "
                + twoDigit(dt.getHours()) + ":"
                + twoDigit(dt.getMinutes()) + ":"
                + twoDigit(dt.getSeconds());
	return "yt-dl-ext " + datetime + ": ";
}

function twoDigit(n){
	return n < 10 ? '0' + n : '' + n ;
}

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
		console.log(getConsoleLogPrefix() + "Disconnected from native app with error: " + p.error);
		msg = "Error: " + p.error;
	} else {
		console.log(getConsoleLogPrefix() + "Disconnected from native app");
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
			+ clickedTab.url;
	} else {
		title = tabs.length + " videos";
		msg = tabs.length + "\n"
			+ title + "\n";
		for (let tab of tabs) {
			msg = msg
				+ tab.url + "\n";
		}
	}
	console.log(getConsoleLogPrefix() + "Sending to native app: " + title);
	port.postMessage(msg);
	createNotification(notificationPrefix + "Download starting", title, startDlNotificationTimeout);
}

function processLink(link) {
	connectNative();
	var msg = 1 + "\n"
		+ link + "\n"
		+ link;
	console.log(getConsoleLogPrefix() + "Sending to native app: " + link);
	port.postMessage(msg);
	createNotification(notificationPrefix + "Download starting", link, startDlNotificationTimeout);
}

// function processStorageChange(changes, area) {
// 	connectNative();
// 	console.log(getConsoleLogPrefix() + "Extra command-line arguments change");
// 
// 	var msg = "^%Extra command-line arguments change" + "\n";
// 
// 	var changedItems = Object.keys(changes);
// 
// 	for (let item of changedItems) {
// 		msg = msg + item + "\n"
// 			  + changes[item].newValue + "\n";
// 	}
// 	console.log(getConsoleLogPrefix() + "Changes: " + msg);
// 	port.postMessage(msg);
// }

function onNativeAppMessage(response) {
	// special messages begin with ^%
	if ( response.substring(0,2) != '^%' ) {
		console.log(getConsoleLogPrefix() + "Native app said: " + response);
		return;
	}
	response = response.substring(2);
	switch (true) {
		case /^Finished downloading /.test(response):
			var title = response.substring("Finished downloading ".length);
			createNotification(notificationPrefix + "Download finished", title, 7000);
			break;
		case /^Failed downloading /.test(response):
			var title = response.substring("Failed downloading ".length);
			createNotification(notificationPrefix + "Failed downloading", "Failed: " + title, 8000);
			break;
		default:
			console.log(getConsoleLogPrefix() + "ERROR: unknown message from native app");
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


