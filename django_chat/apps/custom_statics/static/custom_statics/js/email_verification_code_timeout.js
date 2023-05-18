var evct = document.getElementById("resend_evc");
var resend_a = document.getElementById("resend_a");
var evct_timeout = +(evct.getAttribute('value'));
var evct_interval = null;
var send_link = null;

function update_email_verification_timeout() {
	if (evct_timeout == 0) {
		evct.innerHTML = "";
		resend_a.setAttribute('href', send_link);
		clearInterval(evct_interval);
		return;
	}

	evct_timeout -= 1;
	evct.innerHTML = " (" + evct_timeout.toString() + "s)";
}

if (evct_timeout) {
	send_link = resend_a.getAttribute('href');
	resend_a.setAttribute('href', '#');
	update_email_verification_timeout();
	evct_interval = setInterval(update_email_verification_timeout, 1000);
}