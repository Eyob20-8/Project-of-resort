
"use strict";

document.addEventListener("DOMContentLoaded", function () {

    // ==========================================
    // 1. HAMBURGER MENU
    // ==========================================
// ==========================================
// 1. HAMBURGER MENU
// ==========================================

    const menuIcon = document.getElementById("menu-icon");
    const menuList = document.getElementById("menu-list");
    const backLink = document.getElementById("malo-link");

    if (!menuIcon || !menuList) {
        console.error("Menu icon or menu list was not found.");
        return;
    }

    function openMenu() {
        menuList.classList.remove("hidden");
        menuIcon.setAttribute("aria-expanded", "true");
    }

    function closeMenu() {
        menuList.classList.add("hidden");
        menuIcon.setAttribute("aria-expanded", "false");
    }

    function toggleMenu(event) {
        event.preventDefault();
        event.stopPropagation();

        if (menuList.classList.contains("hidden")) {
            openMenu();
        } else {
            closeMenu();
        }
    }

    // Initialize the menu as closed
    closeMenu();

    // Make the hamburger icon keyboard accessible
    menuIcon.style.cursor = "pointer";
    menuIcon.setAttribute("role", "button");
    menuIcon.setAttribute("tabindex", "0");
    menuIcon.setAttribute("aria-controls", "menu-list");

    // Click the main hamburger icon
    menuIcon.addEventListener("click", toggleMenu);

    // Support Enter and Space keys
    menuIcon.addEventListener("keydown", function (event) {
        if (event.key === "Enter" || event.key === " ") {
            toggleMenu(event);
        }
    });

    // Close using the Menu icon inside the dropdown
    if (backLink) {
        backLink.addEventListener("click", function (event) {
            event.preventDefault();
            event.stopPropagation();
            closeMenu();
        });
    }

    // Keep clicks inside the dropdown from reaching document
    menuList.addEventListener("click", function (event) {
        event.stopPropagation();
    });

    // Close when clicking anywhere outside the menu
    document.addEventListener("click", function (event) {
        if (
            !menuList.contains(event.target) &&
            !menuIcon.contains(event.target)
        ) {
            closeMenu();
        }
    });

    // Close with Escape
    document.addEventListener("keydown", function (event) {
        if (event.key === "Escape") {
            closeMenu();
        }
    });

    console.log("Hamburger menu initialized successfully.");
    document.querySelectorAll(".Event").forEach(function (link) {
        link.addEventListener("click", function (event) {
            event.preventDefault();
            alert("Upcoming event...");
        });
    });
   

    // ==========================================
    // 2. ADULT AND CHILD COUNTERS
    // ==========================================

    document.querySelectorAll(".counter-btn").forEach(function (button) {
        button.addEventListener("click", function () {
            const targetId = button.dataset.target;
            const change = Number(button.dataset.change);
            const input = document.getElementById(targetId);

            if (!input || !Number.isFinite(change)) return;

            const min = Number(input.min || 0);
            const max = Number(input.max || 999);
            const current = Number(input.value || 0);

            input.value = Math.max(
                min,
                Math.min(max, current + change)
            );

            input.dispatchEvent(new Event("change", {
                bubbles: true
            }));
        });
    });

    // ==========================================
    // 3. CHECK AVAILABILITY FORM
    // ==========================================

    const form = document.getElementById("availability-form");
    const adultInput = document.getElementById("adult");
    const childInput = document.getElementById("child");
    const dateInput = document.getElementById("date");
    const errorMsg = document.getElementById("error-msg");
    const totalMsg = document.getElementById("total-msg");

    function getLocalDate() {
        const now = new Date();

        const year = now.getFullYear();
        const month = String(now.getMonth() + 1).padStart(2, "0");
        const day = String(now.getDate()).padStart(2, "0");

        return `${year}-${month}-${day}`;
    }

    if (dateInput) {
        dateInput.min = getLocalDate();
    }

    if (form) {
        form.addEventListener("submit", function (event) {
            event.preventDefault();

            if (errorMsg) errorMsg.textContent = "";
            if (totalMsg) totalMsg.textContent = "";

            const adults = Number(adultInput?.value);
            const children = Number(childInput?.value);
            const checkin = dateInput?.value;

            if (
                !adultInput ||
                !childInput ||
                !dateInput ||
                !Number.isInteger(adults) ||
                !Number.isInteger(children) ||
                adults < 1 ||
                adults > 10 ||
                children < 0 ||
                children > 4
            ) {
                if (errorMsg) {
                    errorMsg.textContent = "Please enter valid guest numbers.";
                }
                return;
            }

            if (!checkin) {
                if (errorMsg) {
                    errorMsg.textContent = "Please select your check-in date.";
                }

                dateInput?.focus();
                return;
            }

            if (checkin < getLocalDate()) {
                if (errorMsg) {
                    errorMsg.textContent = "Check-in date cannot be in the past.";
                }
                return;
            }

            if (totalMsg) {
                totalMsg.textContent =
                    `Search details: ${adults} adult(s), ` +
                    `${children} child(ren), check-in ${checkin}. ` +
                    "Your details are valid. Live room availability " +
                    "must be checked by the server.";
            }

            console.log("Availability form validated:", {
                adults: adults,
                children: children,
                checkin: checkin
            });
        });
    }

    console.log("Kedamawi Resort JavaScript loaded.");
});
