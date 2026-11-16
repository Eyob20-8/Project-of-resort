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

document.addEventListener("DOMContentLoaded", function () {
    const passwordInput = document.getElementById("loginPassword");
    const togglePassword = document.getElementById("togglePassword");
    const loginForm = document.getElementById("play");
    const submitButton = document.getElementById("submit");

    // Show or hide the password.
    if (passwordInput && togglePassword) {
        togglePassword.addEventListener("click", function () {
            const isPassword = passwordInput.type === "password";

            passwordInput.type = isPassword ? "text" : "password";

            togglePassword.innerHTML = isPassword
                ? '<i class="fa-regular fa-eye-slash"></i>'
                : '<i class="fa-regular fa-eye"></i>';

            togglePassword.setAttribute(
                "aria-label",
                isPassword ? "Hide password" : "Show password"
            );

            togglePassword.setAttribute(
                "aria-pressed",
                String(isPassword)
            );
        });
    }

    // Prevent accidental double-clicks while submitting.
    // The browser still sends the form to Flask normally.
    if (loginForm && submitButton) {
        loginForm.addEventListener("submit", function () {
            submitButton.disabled = true;
            submitButton.innerHTML =
                'Logging in <i class="fa-solid fa-spinner fa-spin"></i>';
        });
    }
});