document.addEventListener("DOMContentLoaded", function () {
    // Password protection for testing purposes
    const password = "test123";
    let enteredPassword = prompt("Enter password to access the site:");
    if (enteredPassword !== password) {
        alert("Incorrect password. Access denied.");
        document.body.innerHTML = "<h2>Access Denied</h2>";
        return;
    }

    // Ensure dropdowns do not duplicate options
    function clearDropdown(dropdown) {
        while (dropdown.options.length > 0) {
            dropdown.remove(0);
        }
    }

    // File Upload and Parsing
    document.getElementById("fileUpload").addEventListener("change", function (event) {
        const file = event.target.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = function (e) {
            const text = e.target.result;
            const questionMatch = text.match(/\*\* Question: \*\*(.*?)\n/);
            const essayMatch = text.match(/\*\* Essay: \*\*(.*)/s);

            const questionBox = document.getElementById("questionBox");
            const essayBox = document.getElementById("essayBox");

            questionBox.value = questionMatch ? questionMatch[1].trim() : "";
            essayBox.value = essayMatch ? essayMatch[1].trim() : "";
            
            questionBox.removeAttribute("readonly");
            essayBox.removeAttribute("readonly");
        };
        reader.readAsText(file);
    });

    // Enable manual text input in question and essay fields
    document.getElementById("questionBox").removeAttribute("readonly");
    document.getElementById("essayBox").removeAttribute("readonly");

    // Form Validation & Submission
    document.getElementById("submitBtn").addEventListener("click", function () {
        const email = document.getElementById("emailInput").value;
        if (!email.includes("@")) {
            alert("Please enter a valid email address.");
            return;
        }

        const question = document.getElementById("questionBox").value;
        const essay = document.getElementById("essayBox").value;
        
        if (!question || !essay) {
            alert("Both Question and Essay fields must be filled.");
            return;
        }

        document.getElementById("reportLink").value = "Processing...";
        fetch("https://example.com/api/process", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, question, essay })
        })
        .then(response => response.json())
        .then(data => {
            document.getElementById("reportLink").value = data.reportLink || "Error processing request.";
        })
        .catch(() => {
            document.getElementById("reportLink").value = "Failed to process submission.";
        });
    });

    // Hover effect
    document.querySelectorAll("button").forEach(button => {
        button.addEventListener("mouseover", function () {
            this.style.opacity = "0.8";
        });
        button.addEventListener("mouseout", function () {
            this.style.opacity = "1";
        });
    });
});
