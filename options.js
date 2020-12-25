var video;
var music;
var podcast;
var global;
var saved;

function saveOptions(e) {
	browser.storage.sync.set({
		video: video.value,
		music: music.value,
		podcast: podcast.value,
		global: global.value
	});
	e.preventDefault();
	saved.innerText = "Saved!";
}

const clearTextSaved = function(e) {
	saved.innerText = "";
}

function restoreOptions() {
	video = document.getElementById("video");
	video.addEventListener('input', clearTextSaved);
	music = document.getElementById("music");
	music.addEventListener('input', clearTextSaved);
	podcast = document.getElementById("podcast");
	podcast.addEventListener('input', clearTextSaved);
	global = document.getElementById("global");
	global.addEventListener('input', clearTextSaved);

	saved = document.getElementById("saved");
	
	var gettingItem = browser.storage.sync.get(['video', 'music', 'podcast', 'global']);
	gettingItem.then((res) => {
		video.value = res.video || '';
		music.value = res.music || '';
		podcast.value = res.podcast || '';
		global.value = res.global || '';
	});
}

document.addEventListener('DOMContentLoaded', restoreOptions);
document.querySelector("form").addEventListener("submit", saveOptions);


