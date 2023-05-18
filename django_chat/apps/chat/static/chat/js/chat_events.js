var search_username_timeout = null;
var BS_THEME = "light"

function truncate_string(s, len = 24) {
	if (s.length > len) {
		s = s.slice(0, len) + "...";
	}

	return s;
}

function search_username_success() {

}

function search_username_fail(msg = "User doesn't exist") {
	let user_search_box = $("div#id_user_search_box");
	user_search_box[0].innerHTML = '<p class = "text-center">' + msg + '</p>'
}

function on_search_username_success(response) {
	json_data = JSON.parse(response)

	if (json_data.result == "OK") {
		let user_search_box = $("div#id_user_search_box");
		user_search_box[0].innerHTML = "";
		let user_count = json_data.users.length;

		for (let i = 0; i < user_count; i++) {
			let user_btn = document.createElement("button");
			let user_image = document.createElement("img");
			let user_name = document.createElement("span");

			user_btn.classList.add("btn");
			user_btn.classList.add("btn-outline-secondary");
			user_btn.classList.add("text-start");
			user_btn.classList.add("w-100");
			user_btn.style.height = "40px";

			user_image.setAttribute("src", json_data.users[i].userimage);
			user_image.classList.add("img-fluid");
			user_image.classList.add("rounded-circle");
			user_image.style.width = "28px";

			user_name.innerHTML = json_data.users[i].username;
			user_name.classList.add("ms-2");

			user_btn.appendChild(user_image);
			user_btn.appendChild(user_name);

			user_search_box[0].appendChild(user_btn);
		}
	} else {
		if (json_data.users.length == 0) {
			search_username_fail();
		}
	}
}

// Idk what arguments this accepts
function on_seach_username_fail(__err, _1, _2) {
	search_username_fail("Network Error!");
}

function search_username() {
	let __username = $("input#id_s_username")[0].value;
	$.ajax({
		url: "/chat/search_user",
		type: "POST",
		data: {
			"username" : __username
		},

		success: on_search_username_success
	});
}

function trigger_search_username(search_bar) {
	if (search_username_timeout) {
		clearTimeout(search_username_timeout);
	}

	let user_search_box = $("div#id_user_search_box");
	let user_chat_box = $("div#id_user_chat_box");

	if (search_bar.value == "") {
		user_search_box[0].classList.add("d-none");
		user_chat_box[0].classList.remove("d-none");
		return;
	}

	user_search_box[0].classList.remove("d-none");
	user_chat_box[0].classList.add("d-none");

	user_search_box[0].innerHTML = '<p class = "text-center">Searching...</p>'

	search_username_timeout = setTimeout(search_username, 1000);
}

function create_chat_button(chat_data) {
	let user_chat_box = $("div#id_user_chat_box");

	let user_btn = document.createElement("button");
	let user_image = document.createElement("img");
	let user_name = document.createElement("span");
	let last_message = document.createElement("p");

	user_btn.classList.add("btn");
	user_btn.classList.add("btn-" + BS_THEME);
	user_btn.classList.add("text-start");
	user_btn.classList.add("w-100");
	user_btn.classList.add("d-flex");
	user_btn.classList.add("align-items-center");
	user_btn.style.height = "56px";
	user_btn.id = "id_chat_" + String(chat_data.chat_id);

	user_image.setAttribute("src", chat_data.userimage);
	user_image.classList.add("img-fluid");
	user_image.classList.add("rounded-circle");
	user_image.classList.add("me-2");
	user_image.style.width = "28px";

	let right_div = document.createElement("div");
	right_div.classList.add("overflow-none")

	user_name.innerHTML = chat_data.username;

	last_message.innerHTML = truncate_string(chat_data.last_message);
	last_message.classList.add("text-muted");
	last_message.classList.add("lh-1");
	last_message.classList.add("my-0");
	// last_message.classList.add("text-truncate");
	last_message.style.fontSize = "0.8em";

	user_btn.appendChild(user_image);
	user_btn.appendChild(right_div)
	right_div.appendChild(user_name);
	right_div.appendChild(document.createElement("br"));
	right_div.appendChild(last_message);

	user_chat_box[0].appendChild(user_btn);
}

function update_chat_button(chat_data) {
	let user_chat_box = $("div#id_user_chat_box");
	let chat_btn = $("button#id_chat_" + String(chat_data.chat_id));
	if (chat_btn.length == 0) {
		create_chat_button(chat_data);
		return;
	}

	chat_btn.find("p")[0].innerHTML = truncate_string(chat_data.last_message);
}

function get_chats_fail(msg = "No Chats") {
	let user_chat_box = $("div#id_user_chat_box");
	user_chat_box[0].innerHTML = '<p class = "text-center">' + msg + '</p>'
}

function on_get_chats_success(response) {
	let json_data = JSON.parse(response);

	if (json_data.result == "OK") {
		let user_chat_box = $("div#id_user_chat_box");
		user_chat_box[0].innerHTML = "";
		let chat_count = json_data.chats.length;

		for (let i = 0; i < chat_count; i++) {
			create_chat_button(json_data.chats[i]);
		}
	} else {
		get_chats_fail();
	}
}

function on_get_chats_fail(__err, __1, __2) {
	get_chats_fail("Networking Error!");
}

function get_chats() {
	$.ajax({
		url: "/chat/get_chats",
		type: "GET",

		success: on_get_chats_success,
		error: on_get_chats_fail
	});
}

function chat_events_init() {
	let chat_container = $("#id_chat_container");
	chat_container.height(window.innerHeight - chat_container.position()["top"]);
	BS_THEME = document.body.getAttribute("data-bs-theme");
	if (BS_THEME == null) BS_THEME = "light";
	get_chats();
}

chat_events_init();