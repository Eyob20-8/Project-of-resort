const regform= document.getElementById("start");
if (regform){
  regform.addEventListener("submit",function(e){
    const name=document.getElementById("Username").value;
    const passkey=document.getElementById("Password").value;
    const confirmpasskey=document.getElementById("Confirmpassword").value;
    if(!name||!passkey||!confirmpasskey){
      alert("Fill all filed");
      return;
    }else if(passkey!==confirmpasskey)
      {alert("passwords doesn't match");
      return;
    }
    function validateEmail(email) {
      // A standard regex pattern for checking emails
       const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
       return regex.test(email);
     }
     // Example usage:
     const emailInput = document.getElementById("Email").value;
     if (!validateEmail(emailInput)) {
         alert("Please enter a valid email address.");
      }
});
}