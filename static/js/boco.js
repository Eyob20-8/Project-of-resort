document.addEventListener("DOMContentLoaded", function(){
// Get DOM elements
const adultInput = document.getElementById("adult");
const childInput = document.getElementById("child");
const dateInput = document.getElementById("date");
const bookBtn = document.getElementById("book-btn");
const errorMsg = document.getElementById("error-msg");
const totalMsg = document.getElementById("total-msg");

// Example prices
const adultPrice = 100;
const childPrice = 50;

bookBtn.addEventListener("click", () => {
    errorMsg.textContent = "";
    totalMsg.textContent = "";

    const adults = parseInt(adultInput.value);
    const children = parseInt(childInput.value);
    const date = dateInput.value;

    // Validation
    if (!date) {
        errorMsg.textContent = "Please select a date!";
        return;
    }
    if (adults < 1 || adults > 10) {
        errorMsg.textContent = "At least 1 adult is required.";
        return;
    }
    if (children <= 0) {
        errorMsg.textContent = "Child count cannot be negative.";
        return;
    }

    // Calculate total price
    const total = adults * adultPrice + children * childPrice;
    //totalMsg.innerHTML = "Total price: $" + total;
    totalMsg.innerHTML ="Book now" 
});
});
document.addEventListener("DOMContentLoaded", function() {
  const menuIcon = document.getElementById("menu-icon");
  const menuList = document.getElementById("menu-list");
  const backButton = document.getElementById("malo");

  menuIcon.addEventListener("click", function() {
    menuList.classList.toggle("hidden");
  });
    //const menuItems = menuList.querySelectorAll("li");
    backButton.addEventListener("click", function(Event) {
    Event.preventDefault();

    menuList.classList.add("hidden"); // close menu
    });
    window.addEventListener("click", function(event) {
    // Check if the menu is currently open
    if (!menuList.classList.contains("hidden")) {
      // If the click happened OUTSIDE the menu list AND OUTSIDE the menu icon, close it
      if (!menuList.contains(event.target) && !menuIcon.contains(event.target)) {
        menuList.classList.add("hidden");
      }
    }
  });
});
  
document.addEventListener("DOMContentLoaded", function() {
    const Evt=document.querySelectorAll("li.Event");
    Evt.forEach(function(item){
        item.addEventListener("click",function(){
            alert(`Upcoming....`);
        });
    });
});
 