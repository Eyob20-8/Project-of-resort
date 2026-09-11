
let btn = document.getElementById("begin");
let arr = JSON.parse(localStorage.getItem("element")) || [];

const today = new Date().toISOString().split('T')[0];
const checkinInput = document.getElementById("datea");
const checkoutInput = document.getElementById("dateb");
checkinInput.min = today;
checkinInput.value = today; 



btn.addEventListener("submit", function(e) {
     let name = document.getElementById("Name").value;
     let gmail = document.getElementById("google").value;
     let adult = document.getElementById("numbera").value;
     let child = document.getElementById("numberb").value;
     let checkin = checkinInput.value;
     let checkout = checkoutInput.value;
     let selectedRoomRadio = document.querySelector('input[name="room_type"]:checked');
     
     const max = 400;
     const min = 300;
     let join = new Date(checkin);
     let leave = new Date(checkout);
     let found = false;
     let count = 0;
     let code;
     let mature = 100;
     let children = 50;

     
     // Added check to prevent NaN if dates are missing
     const diff = (checkin && checkout) ? (leave - join) / (1000 * 60 * 60 * 24) : 0;

     // 1. Validation Checks (Stop form submission if invalid)
     if (!name || !checkin || !checkout || !gmail) {
        e.preventDefault(); // Stop Flask from submitting
        alert(`Please fill all fields!`);
        return;
     } else if (!selectedRoomRadio) {
        e.preventDefault(); 
        alert(`Please choose a room type !`);
        return;
     } else if (diff < 1) {
        e.preventDefault(); // Stop Flask from submitting
        alert(`Incorrect Date!`);
        return;
     }
     let cost = diff * ((adult * mature) + (children * child));
     btn.submit();
     // Look for the hidden element containing our room data
      const alertDataElement = document.getElementById("room-alert-data");
      // If the element exists on the page, grab the room number and alert the user
      if (alertDataElement) {
         const roomNumber = alertDataElement.getAttribute("data-room");
         const guest = alertDataElement.getAttribute("data-name")
         alert(`Welcome ${guest}\nRoom number:${roomNumber}\nEnjoy your time!`);
      }
   });

function unchooseItem(labelElement) {
    const radioButton = labelElement.querySelector('input[type="radio"]');
    setTimeout(() => {
        radioButton.checked = false;
    }, 10);
};
