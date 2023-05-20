var search_username_timeout = null;
var BS_THEME = "light"
var current_user_name = null;
var current_user_id = null;
var current_chat_id = null;
var chat_list_open = false;

var chat_message_node = null;

function truncate_string(s, len = 24) {
	if (s.length > len) {
		s = s.slice(0, len) + "...";
	}

	return s;
}

function toggle_chat_list() {
	let chat_list = $("#id_chat_list")[0];

	if (chat_list_open) {
		chat_list.classList.add("d-none");
		chat_list_open = false;
	} else {
		chat_list.classList.remove("d-none");
		chat_list_open = true;
	}
}

function chat_socket_opened() {
	chat_socket_open = true;
}

function clear_chat_messages() {
	let messages = $("#id_messages")[0];
	messages.innerHTML = "";
}

function scroll_messages_down() {
	mscroll = $("#id_messages_scroll")[0];
	mscroll.scroll(0, mscroll.scrollHeight);
}

function add_chat_message(sender_name, message_text, is_me = false, sent_date) {
	let chat_message = chat_message_node.cloneNode(true);
	let messages = $("#id_messages")[0];

	let __spans = chat_message.getElementsByTagName("span");
	let __span1 = __spans[0];
	let __span2 = __spans[1];
	__span1.innerHTML = message_text;

	if (is_me) {
		chat_message.classList.add("align-items-end");
		__span1.classList.add('text-light');
		chat_message.getElementsByTagName("div")[0].classList.add('bg-secondary')
	}

	let __sent_date = new Date(sent_date * 1000); // convert to milliseconds, because js works with milliseconds
	let __hours = String(__sent_date.getHours());
	let __minutes = String(__sent_date.getMinutes());
	let __month = __sent_date.toLocaleString('en', {month: "short"});
	let __day = __sent_date.getDate();

	if (__hours.length < 2) {
		__hours = "0" + __hours;
	}
	if (__minutes.length < 2) {
		__minutes = "0" + __minutes;
	}

	let __time = __hours + ":" + __minutes;

	let __today = new Date();
	if (__today.getDate() != __day) {
		__time = __month + "/" + String(__day) + " " + __time;
	}

	__span2.innerHTML = __time
	messages.appendChild(chat_message);
	scroll_messages_down();
}

function clear_search_username() {
	s_username = $("#id_s_username")[0];
	s_username.value = "";
	trigger_search_username(s_username);
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
			user_btn.setAttribute("onclick", 'searched_user(this.value, "userid")');
			user_btn.setAttribute("value", json_data.users[i].userid);

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
	user_btn.setAttribute("onclick", 'get_messages(this.value, "chat_id")');
	user_btn.setAttribute("value", chat_data.chat_id);

	user_image.setAttribute("src", chat_data.userimage);
	user_image.classList.add("img-fluid");
	user_image.classList.add("rounded-circle");
	user_image.classList.add("me-2");
	user_image.style.width = "28px";

	let right_div = document.createElement("div");
	right_div.classList.add("overflow-none")

	user_name.innerHTML = chat_data.username;

	last_message.innerHTML = truncate_string(chat_data.last_message);
	if (chat_data.sender_id == current_user_id) {
		last_message.classList.add("text-muted");
	}
	last_message.classList.add("lh-1");
	last_message.classList.add("my-0");
	last_message.style.fontSize = "0.8em";

	user_btn.appendChild(user_image);
	user_btn.appendChild(right_div)
	right_div.appendChild(user_name);
	right_div.appendChild(document.createElement("br"));
	right_div.appendChild(last_message);

	user_chat_box[0].appendChild(user_btn);

	/*****************************/

	chat_socket.send(JSON.stringify({
		method: "add_chat_room",
		chat_id: chat_data.chat_id
	}))

	/*****************************/

	return user_btn
}

function update_chat_button(chat_data) {
	let user_chat_box = $("div#id_user_chat_box");
	let chat_btn = $("button#id_chat_" + String(chat_data.chat_id));
	if (chat_btn.length == 0) {
		chat_btn = create_chat_button(chat_data);
		return;
	}
	let last_message = chat_btn.find("p")[0];
	last_message.innerHTML = truncate_string(chat_data.last_message);
	if (chat_data.sender_id == current_user_id) {
		last_message.classList.add("text-muted");
	} else {
		last_message.classList.remove("text-muted");
	}
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
			update_chat_button(json_data.chats[i]);
		}
	} else {
		get_chats_fail();
	}
}

function on_get_chats_fail(__err, __1, __2) {
	get_chats_fail("Network Error!");
}

function get_chats() {
	$.ajax({
		url: "/chat/get_chats",
		type: "GET",

		success: on_get_chats_success,
		error: on_get_chats_fail
	});
}

function get_messages_fail(msg = "No Messages Yet") {
	console.log("get_messages error");
}

function on_get_messages_fail(__err, __1, __2) {
	get_messages_fail("Network Error!")
}

function on_get_messages_success(response) {
	console.log(response);
	let json_data = JSON.parse(response);

	let message_input = $("#id_message_input")[0];
	message_input.classList.remove("d-none");

	clear_chat_messages();
	current_chat_id = json_data.chat_id;

	for (let i = 0; i < json_data.messages.length; i++) {
		let message_sent_date = json_data.messages[i].sent_date;
		let message_text = json_data.messages[i].text;
		let message_sender = json_data.messages[i].sender;

		add_chat_message("", message_text, (message_sender == current_user_id), message_sent_date);
	}

	scroll_messages_down();
}

function get_messages(__value, __key) {
	__data = {};
	__data[__key] = __value;

	$.ajax({
		url: "/chat/get_messages",
		type: "POST",
		data: __data,

		success: on_get_messages_success,
		error: on_get_messages_fail,
	});
}

function send_message(message_text) {
	let data_to_send = JSON.stringify({
		method: "send_message",
		sender_id: current_user_id,
		chat_id: current_chat_id,
		text: message_text
	});

	chat_socket.send(data_to_send);
}

function send_message_from_input() {
	let message_input = $("#id_message_input")[0].getElementsByTagName("input")[0];
	if (message_input.value == "") return;
	send_message(message_input.value);
	message_input.value = "";
}

function searched_user(__value, __key) {
	clear_search_username();
	get_chats();
	get_messages(__value, __key);
}

var __chat_events_init_interval = null;
function chat_events_init() {
	if (!chat_socket.OPEN) return;

	let chat_container = $("#id_chat_container");
	chat_container.height(window.innerHeight - chat_container.position()["top"]);
	BS_THEME = document.body.getAttribute("data-bs-theme");
	if (BS_THEME == null) BS_THEME = "light";
	current_user_name = document.getElementById("id_current_username").getAttribute("value");
	current_user_id = Number(document.getElementById("id_messages").getAttribute("value"));

	// chat_message_node = document.createElement("div");
	// chat_message_node.classList.add("w-100");
	// chat_message_node.classList.add("d-flex");
	// chat_message_node.classList.add("flex-column");

	// chat_message_node_card = document.createElement("div");
	// chat_message_node_card.classList.add("card");
	// chat_message_node_card.classList.add("mx-3");
	// chat_message_node_card.classList.add("my-1");
	// chat_message_node_card.style.maxWidth = "75%";
	// chat_message_node_card.style.width = "fit-content";

	// chat_message_node_body = document.createElement("div");
	// chat_message_node_body.classList.add("card-body");
	// chat_message_node_body.style.paddingTop = "0.25em";
	// chat_message_node_body.style.paddingBottom = "0.25em";
	// chat_message_node_body.appendChild(document.createElement("span"));

	// chat_message_node_card.appendChild(chat_message_node_body);
	// chat_message_node.appendChild(chat_message_node_card);

	chat_message_node = $(
		`
		<div class="w-100 d-flex flex-column">
			<div class="card mx-3 my-1" style="max-width: 75%; width: fit-content;">
				<div class="card-body" style="padding-top: 0.25em; padding-bottom: 0.25em;">
					<span></span>
					<br/>
					<span style = "font-size: 0.75em"><i>23:59</i></span>
				</div>
			</div>
		</div>
		`
	)[0];

	$("#id_message_input")[0].getElementsByTagName("input")[0].onkeyup = function(e) {
		if (e.keyCode == 13) {
			send_message_from_input();
		}
	};

	get_chats();

	clearInterval(__chat_events_init_interval);
}

__chat_events_init_interval = setInterval(chat_events_init, 500);

const chat_socket = new WebSocket("ws://" + window.location.host + "/");

chat_socket.onopen = function (e) {
	console.log("The connection was setup successfully !");
};

chat_socket.onclose = function (e) {
	console.log("Something unexpected happened !");
};

chat_socket.onmessage = function (e) {
	let json_data = JSON.parse(e.data);

	if (json_data.type == "add_chat_message") {
		update_chat_button({chat_id: json_data.chat_id, last_message: json_data.text, sender_id: json_data.sender_id});
		if (json_data.chat_id == current_chat_id) {
			add_chat_message("", json_data.text, (json_data.sender_id == current_user_id), json_data.sent_date);
		}
	}
}