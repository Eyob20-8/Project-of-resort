document.getElementById("ended").addEventListener("click", async function () {

    const textarea = document.getElementById("comment");
    const comment = textarea.value.trim();

    // Check if empty
    if (!comment) {
        alert("Please enter your feedback.");
        return;
    }

    try {

        const response = await fetch("/feedback", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                comment: comment
            })
        });

        const data = await response.json();

        if (data.success) {
            alert("Feedback submitted successfully!");
            textarea.value = "";
        } else {
            alert(data.message);
        }

    } catch (error) {
        console.error("Error:", error);
        alert("Something went wrong.");
    }
});