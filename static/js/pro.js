
document.addEventListener("DOMContentLoaded", function () {
    console.log("=================================");
    console.log("pro.js is loaded");
    console.log("DOM is ready");
    console.log("=================================");

    // =====================================================
    // GET ELEMENTS
    // =====================================================

    const uploadForm = document.getElementById("uploadForm");
    const imageUpload = document.getElementById("imageUpload");
    const profileImage = document.getElementById("profileImage");
    const profileIcon = document.getElementById("profileIcon");
    const profileContainer = document.querySelector(".profile-container");
    const registrationForm = document.getElementById("start");
    const verify = document.getElementById("verify");

    let currentPreviewURL = null;

    console.log("Image input found:", !!imageUpload);
    console.log("Profile image found:", !!profileImage);
    console.log("Profile icon found:", !!profileIcon);
    console.log("Profile form found:", !!registrationForm);

    // =====================================================
    // 1. PROFILE IMAGE PREVIEW AND UPLOAD
    // =====================================================

    if (imageUpload && profileImage && profileIcon) {
        imageUpload.addEventListener("change", async function () {
            console.log("Image input changed.");

            const file = imageUpload.files[0];

            if (!file) {
                console.log("No file selected.");
                return;
            }

            console.log("Selected image:", file.name);
            console.log("Image type:", file.type);
            console.log("Image size:", file.size);

            // Validate image type
            const allowedTypes = [
                "image/png",
                "image/jpeg",
                "image/gif",
                "image/webp"
            ];

            if (!allowedTypes.includes(file.type)) {
                alert("Please select a PNG, JPG, GIF, or WebP image.");
                imageUpload.value = "";
                return;
            }

            // Maximum image size: 5 MB
            const maxSize = 5 * 1024 * 1024;

            if (file.size > maxSize) {
                alert("Image must be smaller than 5 MB.");
                imageUpload.value = "";
                return;
            }

            // Display the preview immediately
            if (currentPreviewURL) {
                URL.revokeObjectURL(currentPreviewURL);
            }

            currentPreviewURL = URL.createObjectURL(file);

            profileImage.src = currentPreviewURL;
            profileImage.style.display = "block";
            profileImage.classList.remove("hidden");
            profileIcon.classList.add("hidden");

            console.log("Image preview displayed.");

            // Upload the image separately from profile details
            const imageData = new FormData();
            imageData.append("file", file);

            try {
                console.log("Uploading image to Flask...");

                const response = await fetch(uploadForm.action, {
                    method: "POST",
                    body: imageData
                });

                console.log("Upload HTTP status:", response.status);

                const contentType =
                    response.headers.get("content-type") || "";

                if (!contentType.includes("application/json")) {
                    throw new Error(
                        "The upload route did not return JSON. Check Flask."
                    );
                }

                const data = await response.json();

                console.log("Upload response:", data);

                if (!response.ok || data.status !== "success") {
                    throw new Error(
                        data.message || "Image upload failed."
                    );
                }

                // Show the permanent saved image
                if (data.url) {
                    profileImage.src = data.url;
                }

                if (verify) {
                    verify.textContent = "Profile image saved successfully.";
                }

                console.log("Image uploaded successfully!");
                console.log("Database image path:", data.profile_image);
                console.log("Saved image URL:", data.url);

                alert("Image uploaded successfully!");

            } catch (error) {
                console.error("Image upload error:", error);
                alert(error.message || "Unable to upload image.");

                if (verify) {
                    verify.textContent = "Image upload failed.";
                }
            }
        });
    } else {
        console.error(
            "Image upload disabled: one or more image elements are missing."
        );
    }

    // =====================================================
    // 2. PROFILE DETAILS FORM
    // =====================================================

    if (registrationForm) {
        registrationForm.addEventListener("submit", async function (event) {
            event.preventDefault();

            const passwordField =
                registrationForm.querySelector('[name="password"]');

            const confirmField =
                registrationForm.querySelector('[name="confirm_password"]'); 
            const email = registrationForm.querySelector('[name="email"]');
            const Fan = registrationForm.querySelector('[name="fan_number"]');
            const username = registrationForm.querySelector('[name="username"]');

            const password = passwordField?.value || "";
            const confirmation = confirmField?.value || "";


            // Check confirmation only if a new password was entered
            if (password !== confirmation) {
                alert("Passwords do not match.");
                return;
            }

            const formData = new FormData(registrationForm);
            try {
                console.log("Submitting profile update...");

                const response = await fetch(registrationForm.action, {
                    method: "POST",
                    body: formData
                });

                console.log("Profile HTTP status:", response.status);

                const contentType =
                    response.headers.get("content-type") || "";

                if (!contentType.includes("application/json")) {
                    throw new Error(
                        "Profile route must return JSON for this JavaScript handler."
                    );
                }

                const result = await response.json();

                console.log("Profile response:", result);

                if (response.ok && result.status === "success") {
                    // Clear ONLY the password fields
                    if (passwordField) {
                        passwordField.value = "";
                    }

                    if (confirmField) {
                        confirmField.value = "";
                    }
                    if(email){
                        email.value = "";
                    }
                    if(Fan){
                        Fan.value = "";
                    }
                    if(username){
                        username.value = "";
                    }

                    console.log("Profile updated successfully.");
                    alert(result.message || "Profile updated successfully!");

                } else {
                    alert(result.message || "Profile update failed.");
                }

            } catch (error) {
                console.error("Profile update error:", error);
                alert(error.message || "Unable to update profile.");
            }
        });
    }

    // =====================================================
    // 3. CLICK PROFILE AREA TO OPEN FILE SELECTOR
    // =====================================================

    if (profileContainer && imageUpload) {
        profileContainer.addEventListener("click", function (event) {
            if (event.target.closest(".upload-overlay")) {
                return;
            }

            if (event.target === imageUpload) {
                return;
            }

            imageUpload.click();
        });
    }

    // =====================================================
    // 4. CLEAN UP TEMPORARY PREVIEW URL
    // =====================================================

    window.addEventListener("beforeunload", function () {
        if (currentPreviewURL) {
            URL.revokeObjectURL(currentPreviewURL);
        }
    });
});