document.addEventListener("DOMContentLoaded", () => {
    const links = document.querySelectorAll(".dynamic-link");
    const displayPanel = document.getElementById("content-display");

    if (!displayPanel) {
        console.error("The content-display element was not found.");
        return;
    }

    // Dynamically load pages into the content panel.
    links.forEach(link => {
        link.addEventListener("click", async function (event) {
            event.preventDefault();

            const targetUrl = this.getAttribute("href");

            if (!targetUrl || targetUrl === "#") return;

            links.forEach(item => item.classList.remove("active"));
            this.classList.add("active");

            try {
                displayPanel.innerHTML = "<p>Loading...</p>";

                const response = await fetch(targetUrl);

                if (!response.ok) {
                    throw new Error(`HTTP error: ${response.status}`);
                }

                const htmlSnippet = await response.text();
                displayPanel.innerHTML = htmlSnippet;

                if (targetUrl.includes("/admin/users")) {
                    await loadUsers();
                } else if (targetUrl.includes("/admin/room")) {
                    // Attach the handler to the newly inserted form.
                    const form = displayPanel.querySelector("#roomSearchForm");

                    if (form) {
                        form.addEventListener("submit", searchroom);
                    }

                    await loadroom();
                } else if (targetUrl.includes("/admin/book")){
                    await book();
                }

            } catch (error) {
                console.error("Failed to load page:", error);

                displayPanel.textContent =
                    `Error loading page: ${error.message}`;
            }
        });
    });

    // Load users into the user management table.
    async function loadUsers() {
        const table = displayPanel.querySelector("#userTable");
        const searchInput = displayPanel.querySelector("#userSearch");

        if (!table) {
            console.error("The userTable element was not found.");
            return;
        }

        try {
            const response = await fetch("/api/admin/users");

            if (!response.ok) {
                throw new Error(`HTTP error: ${response.status}`);
            }

            const users = await response.json();
            

            if (!Array.isArray(users)){
                throw new Error("Expected an array of users.");
            }   

            function displayUsers(filteredUsers) {
                 table.replaceChildren();
                 if (filteredUsers.length === 0) {
                     const row = table.insertRow();
                     const cell = row.insertCell();
                     cell.colSpan = 5;
                     cell.textContent = "No users found.";
                     return;
                }

                filteredUsers.forEach((user, index) => {
                    const row = table.insertRow();
                    row.insertCell().textContent = index + 1;
                    row.insertCell().textContent = user.username ?? "";
                    row.insertCell().textContent = user.email ?? "";
                    row.insertCell().textContent = user.role ?? "";

                    const actions = row.insertCell();

                    const viewButton = document.createElement("button");
                    viewButton.type = "button";
                    viewButton.textContent = "View";
                    viewButton.classList.add("action-btn");
                    const DelButton = document.createElement("button")
                    DelButton.type = "button";
                    DelButton.textContent = 
                         Number(user.is_active)===0
                             ? "Deactivate"
                             : "Reactivate";
                    DelButton.classList.add("action-btn");
                    viewButton.addEventListener("click", () => {
                        alert(
                            `ID: ${user.id}\n` +
                            `Username: ${user.username}\n` +
                            `Email: ${user.email}`
                        );
                    });
                    DelButton.addEventListener("click", async () => {
                    const confirmed = confirm(
                         `Are you sure you want to deactivate ${user.username}?`
                     );

                     if (!confirmed) return;

                     try {
                         const response = await fetch(
                             `/api/admin/users/${user.id}`,
                             { method: "DELETE" }
                         );

                         const result = await response.json();

                         if (!response.ok) {
                             alert(result.message || "Failed to delete user");
                             return;
                         }

                         alert(result.message);

                         // Reload the table after successful deletion
                         loadUsers();

                        } catch (error) {
                             console.error("Delete error:", error);
                             alert("Could not connect to the server.");
                         }
                    });

    
                    actions.appendChild(viewButton);
                    actions.appendChild(DelButton)
                });
            }

                 // Display all users initially.
            displayUsers(users);

                 // Filter users as the administrator types.
            if (searchInput) {
                searchInput.oninput = () => {
                     const query = searchInput.value.trim().toLowerCase();

                     const filteredUsers = users.filter(user =>
                         String(user.username ?? "").toLowerCase().includes(query) ||
                         String(user.email ?? "").toLowerCase().includes(query)
                     );

                     displayUsers(filteredUsers);
                 };
             }
        } catch (error) {
            console.error("Failed to load users:", error);

            table.replaceChildren();
            const row = table.insertRow();
            const cell = row.insertCell();
            cell.colSpan = 5;
            cell.textContent = `Unable to load user ${error.message}.`;
        }
    }

    // Load room counts from the combined Flask API.
    async function loadroom() {
        const total = displayPanel.querySelector("#Total");
        const available = displayPanel.querySelector("#Available");
        const maint = displayPanel.querySelector("#mainten");
        const occupy = displayPanel.querySelector("#Occ");
        const main = displayPanel.querySelector("#mains");

        try {
            const response = await fetch("/api/admin/room");

            if (!response.ok) {
                throw new Error(`HTTP error: ${response.status}`);
            }

            const data = await response.json();

            // The combined API returns counts inside data.count.
            const count = data.count ?? data;

            if (
                count.total === undefined ||
                count.available === undefined ||
                count.occupied === undefined ||
                count.maintenance === undefined
            ) {
                throw new Error("Unexpected room-count response format.");
            }

            if (total) total.textContent = count.total;
            if (available) available.textContent = count.available;
            if (maint) maint.textContent = count.maintenance;
            if (occupy) occupy.textContent = count.occupied;

        } catch (error) {
            console.error("Failed to load rooms:", error);

            if (main) {
                const errorMessage = document.createElement("p");
                errorMessage.textContent =
                    "Unable to load rooms. Please try again.";
                main.appendChild(errorMessage);
            }
        }
    }

    // Search rooms using the same combined API endpoint.
    async function searchroom(event) {
        event.preventDefault();

        const form = event.currentTarget;
        const roomNumberInput = form.querySelector("#room_number");
        const roomTypeInput = form.querySelector("#room_type");
        const results = displayPanel.querySelector("#roomResults");
        const message = displayPanel.querySelector("#searchMessage");

        if (!roomNumberInput || !roomTypeInput || !results || !message) {
            console.error("A room-search form element is missing.");
            return;
        }

        const roomNumber = roomNumberInput.value.trim();
        const roomType = roomTypeInput.value;

        const params = new URLSearchParams({
            room_number: roomNumber,
            room_type: roomType
        });

        message.textContent = "Searching...";
        results.replaceChildren();

        try {
            const response = await fetch(
                `/api/admin/room?${params.toString()}`
            );

            if (!response.ok) {
                throw new Error(`HTTP error: ${response.status}`);
            }

            const data = await response.json();
            const rooms = data.rooms;

            if (!Array.isArray(rooms)) {
                throw new Error("Unexpected room-search response format.");
            }

            if (rooms.length === 0) {
                message.textContent = "No rooms found.";
                return;
            }

            message.textContent = `${rooms.length} room(s) found.`;

            const table = document.createElement("table");
            const thead = document.createElement("thead");
            const headerRow = document.createElement("tr");
            const tbody = document.createElement("tbody");
            [
                 "Room No",
                 "Guest Name",
                 "Room Type",
                 "Availability",
                 "Check-in",
                 "Check-out",
                 "Email"
            ].forEach(label => {
                const th = document.createElement("th");
                th.textContent = label;
                headerRow.appendChild(th);
            });
            thead.appendChild(headerRow)

            rooms.forEach(room => {
                const row = document.createElement("tr");
                const values = [
                     room.Room_No,
                     room.fullname,
                     room.Room_type,
                     room.status,
                     room.checkin,
                     room.checkout,
                     room.email
                 ];
                 values.forEach(value => {
                     const td = document.createElement("td");
                     td.textContent = value ?? "N/A";
                     row.appendChild(td);
                });
                tbody.appendChild(row);
            });
            table.appendChild(thead);
            table.appendChild(tbody);
            results.appendChild(table);q

        } catch (error) {
            console.error("Room search failed:", error);
            message.textContent =
                "Could not load rooms. Please try again.";
        }
    }
    async function book(event) {
        const total = document.getElementById("var");
        const pending = document.getElementById("vandik");
        const cancel = document.getElementById("lol");
        const checkin = document.getElementById("kopa");
        const checkout = document.getElementById("mk");
        const container = document.getElementById("custan")
        try{
             const custom = await fetch ("/api/admin/book");         
             if(!custom){
                 throw new error (`Http reponse:${result.status}`)
             }
             const result = await custom.json();
             if(
                 !Array.isArray(result.customers)||
                 result.total==undefined||
                 result.pending==undefined||
                 result.cancel==undefined
             ){
            throw new error("Unexpected response format")
             }
             if(total)total.textContent =result.total??"__"
             if(pending)pending.textContent=result.pending??"__"
             if(cancel)cancel.textContent=result.cancel??"__"
             if(checkin)checkin.textContent=result.checkin??"__"
             if(checkout)checkout.textContent=result.checkout??"__"
             // Create the table
             const table = document.createElement("table");
             table.style.width = "100%";
             table.style.borderCollapse = "collapse";

             const thead = document.createElement("thead");
             const headerRow = document.createElement("tr");

             ["ID", "Username", "Check-in", "Check-out", "Status"]
                 .forEach(text => {
                     const th = document.createElement("th");
                     th.textContent = text;
                     th.style.padding = "10px";
                     th.style.border = "1px solid #ccc";
                     headerRow.appendChild(th);
                 });

             thead.appendChild(headerRow);
             table.appendChild(thead);

             const tbody = document.createElement("tbody");

             result.customers.forEach(customer => {
                 const row = document.createElement("tr");

                 [
                     customer.id,
                     customer.username,
                     customer.checkin,
                     customer.checkout,
                     customer.status
                 ].forEach(value => {
                     const td = document.createElement("td");

                     // textContent prevents HTML from being interpreted
                     td.textContent = value ?? "";
                     td.style.padding = "10px";
                     td.style.border = "1px solid #ccc";

                     row.appendChild(td);
                 });

                 tbody.appendChild(row);
             });

             table.appendChild(tbody);

             // Replace the previous table
             container.replaceChildren(table);
        }catch (error) {
             console.error("Booking management error:", error);
             container.textContent = "Unable to load booking data.";
             }
    }
     async function payment(event){}
    // Handle clicks on #user even if that element is inserted dynamically.
    document.addEventListener("click", event => {
        const userElement = event.target.closest("#user");

        if (userElement) {
            event.preventDefault();
            loadUsers();
        }
    });

    // Handle existing Event buttons.
document.querySelectorAll(".Event").forEach(element => {
        element.addEventListener("click", event => {
            event.preventDefault();
            alert("Please add events or destination.");
        });
    });
});