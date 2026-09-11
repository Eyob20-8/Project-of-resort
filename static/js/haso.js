const loginForm=document.getElementById("play");
if (loginForm){
  loginForm.addEventListener("submit", function(e) {
    let username = document.getElementById("loginUsername").value.trim();
    let password = document.getElementById("loginPassword").value.trim();
    if (username === "" && password === "") {
      e.preventDefault(); // stops form reload
      alert("Please fill all fileds.")
     }
  });
}