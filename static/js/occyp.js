
const form = document.getElementById("begin");

const checkinInput = document.getElementById("datea");
const checkoutInput = document.getElementById("dateb");

const roomSelect = document.getElementById("room_type");

const today = new Date();
const localToday = [
    today.getFullYear(),
    String(today.getMonth() + 1).padStart(2, "0"),
    String(today.getDate()).padStart(2, "0")
].join("-");

checkinInput.min = localToday;
checkoutInput.min = localToday;

// Update the earliest checkout date when check-in changes.
checkinInput.addEventListener("change", function () {
    checkoutInput.min = checkinInput.value || localToday;

    if (
        checkoutInput.value &&
        checkoutInput.value <= checkinInput.value
    ) {
        checkoutInput.value = "";
    }
});

form.addEventListener("submit", function (event) {
    const name = document.getElementById("Name").value.trim();
    const email = document.getElementById("google").value.trim();
    const adults = Number(document.getElementById("numbera").value);
    const children = Number(document.getElementById("numberb").value);

    const checkin = checkinInput.value;
    const checkout = checkoutInput.value;
    const roomType = roomSelect.value;

    if (!name || !email || !checkin || !checkout || !roomType) {
        event.preventDefault();
        alert("Please complete all required fields.");
        return;
    }

    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        event.preventDefault();
        alert("Please enter a valid email address.");
        return;
    }

    if (adults < 1 || children < 0) {
        event.preventDefault();
        alert("Please enter valid guest numbers.");
        return;
    }

    if (checkin < localToday || checkout <= checkin) {
        event.preventDefault();
        alert("Please select valid check-in and check-out dates.");
        return;
    }

    // Do not call form.submit() here.
    // The browser submits the form normally, and Flask processes it.
});
