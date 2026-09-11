let arr = JSON.parse(localStorage.getItem("element")) || [];

document.addEventListener("DOMContentLoaded", function() {
  // Store the active rating globally within our listener scope
  let currentRating = 0; 

  // 1. STAR RATING SYSTEM
  const stars = document.querySelectorAll('.star-rating span');
  const ratingText = document.getElementById('rating-value');

  stars.forEach(star => {
     star.addEventListener('click', () => {
       // Multiply by 2 matching your 10-point scale logic
       currentRating = parseInt(star.getAttribute('data-value')) * 2; 
       ratingText.textContent = `Rating of: ${currentRating}/10`;
       updateStars(star.getAttribute('data-value'));
     });
  });

  function updateStars(ratingValue) {
     stars.forEach(star => {
       star.classList.remove('filled');
       if (parseInt(star.getAttribute('data-value')) <= ratingValue) {
         star.classList.add('filled');
       }
    });
  }

  // 2. FORM VALIDATION & FLASK POST SUBMISSION
  const fini = document.getElementById("reo");
  if (fini) {
     fini.addEventListener("submit", function(e) {
       e.preventDefault(); // Stop the page from refreshing immediately

       let username = document.getElementById("nam").value.trim();
       let Room_number = document.getElementById("prom").value.trim();
       
       if (username === "" || Room_number === "") {
          alert("Fill all fields.");
          return; // Stop execution
       }

       // Prepare the payload data
       let checkoutData = {
          user: username,
          Room: Room_number,
          rating: currentRating
       };

       // Send data to the Flask route '/submit-checkout' via POST
       fetch('/leave', {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json'
          },
          body: JSON.stringify(checkoutData)
       })
       .then(response => response.json())
       .then(data => {
          if (data.status === 'success') {
              alert(`Goodbye ${username}! Your checkout data has been saved successfully!`);
              document.getElementById("reo").reset();
              // Optional: redirect or reset the form here
          } else {
              alert("Error: " + data.message);
          }
       })
       .catch(err => {
          console.error("Transmission error:", err);
          alert("Could not connect to server.");
       });
     });
  }  
});

