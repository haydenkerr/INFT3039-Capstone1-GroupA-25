document.addEventListener("DOMContentLoaded", function () {
       // -----------------------------------------------------
    // Password protection (remove if not needed)
    // -----------------------------------------------------
    // const password = "test123";
    // let enteredPassword = prompt("Enter password to access the site:");
    // if (enteredPassword !== password) {
    //     alert("Incorrect password. Access denied.");
    //     document.body.innerHTML = "<h2>Access Denied</h2>";
    //     return;
    // }
    // // -----------------------------------------------------
    // (Optional) Populate some dropdowns
    // -----------------------------------------------------
    // const submissionGroup = document.querySelector(".desktop1-submissiongroup select");
    // for (let i = 1; i <= 5; i++) {
    //     let option = document.createElement("option");
    //     option.value = i;
    //     option.textContent = i;
    //     submissionGroup.appendChild(option);
    // }

    // const taskType = document.querySelector(".desktop1-tasktype select");
    // ["Academic Task 1", "Academic Task 2", "General Task 1", "General Task 2"].forEach(task => {
    //     let option = document.createElement("option");
    //     option.value = task;
    //     option.textContent = task;
    //     taskType.appendChild(option);
    // });

    // const generateQuestion = document.querySelector(".desktop1-generatequestion select");
    // ["Yes - I require a question", "No - I will enter or upload a question"].forEach(choice => {
    //     let option = document.createElement("option");
    //     option.value = choice;
    //     option.textContent = choice;
    //     generateQuestion.appendChild(option);
    // });

    // -----------------------------------------------------
    // File Upload and Parsing
    // -----------------------------------------------------
    // Clicking "Choose File" triggers hidden file input
    document.querySelector(".desktop1-uploadfilebutton").addEventListener("click", () => {
        document.getElementById("fileInput").click();
    });

    // Listen for file selection
    document.getElementById("fileInput").addEventListener("change", handleFile);

    function handleFile(e) {
        const file = e.target.files[0];
        if (!file) {
            alert("Please select a file.");
            return;
        }

        // Show filename next to the button
        document.querySelector(".desktop1-input2").value = file.name;

        const extension = file.name.toLowerCase().split(".").pop();

        // .txt -> read as text
        if (extension === "txt") {
            const reader = new FileReader();
            reader.onload = function(ev) {
                const text = ev.target.result;
                parseQuestionEssay(text);  // put question & essay into boxes
                // sendTextToAPI(text);       // optional: send entire text to your API
                debugOutput(text);         // show in #output for debugging
            };
            reader.readAsText(file);
        }
        // .docx -> use mammoth
        else if (extension === "docx") {
            const reader = new FileReader();
            reader.onload = function() {
                mammoth.extractRawText({ arrayBuffer: reader.result })
                    .then(result => {
                        let fullText = result.value;
                        parseQuestionEssay(fullText);
                        // sendTextToAPI(fullText);
                        debugOutput(fullText);
                    })
                    .catch(err => {
                        console.error("Error processing DOCX:", err);
                    });
            };
            reader.readAsArrayBuffer(file);
        }
        // .pdf -> use pdf.js
        else if (extension === "pdf") {
            const reader = new FileReader();
            reader.onload = function() {
                const typedarray = new Uint8Array(reader.result);
                extractTextFromPDF(typedarray)
                    .then(fullText => {
                        parseQuestionEssay(fullText);
                        // sendTextToAPI(fullText);
                        debugOutput(fullText);
                    })
                    .catch(err => {
                        console.error("Error processing PDF:", err);
                    });
            };
            reader.readAsArrayBuffer(file);
        }
        else {
            alert("Unsupported file format. Please upload a TXT, PDF, or DOCX file.");
        }
    }

    // PDF extraction
    function extractTextFromPDF(typedarray) {
        return pdfjsLib.getDocument(typedarray).promise.then(pdf => {
            let text = "";
            const pagePromises = [];
            for (let i = 1; i <= pdf.numPages; i++) {
                pagePromises.push(
                    pdf.getPage(i).then(page =>
                        page.getTextContent().then(tc => {
                            const pageText = tc.items.map(item => item.str).join(" ");
                            text += pageText + "\n";
                        })
                    )
                );
            }
            return Promise.all(pagePromises).then(() => text);
        });
    }

    // -----------------------------------------------------
    // Regex parse: ** Question: ** and ** Essay: **
    // -----------------------------------------------------
    function parseQuestionEssay(fullText) {
        console.log("[parseQuestionEssay] Raw extracted text:", JSON.stringify(fullText));
      
        // Clean up line breaks
        fullText = fullText.replace(/\r\n/g, "\n").replace(/\r/g, "\n");
      
        // More permissive multiline capture:
        // - The first group is "lazy" ([\s\S]+?) so it stops when it sees "** Essay: **"
        // - The second group is "greedy" ([\s\S]+) so it captures everything until the end
        const multiRegex = /\*\*\s*question:\s*\*\*([\s\S]+?)\*\*\s*essay:\s*\*\*([\s\S]+)/i;
        const multiMatch = fullText.match(multiRegex);
      
        let questionBox = document.querySelector(".desktop1-textarea3");
        let essayBox    = document.querySelector(".desktop1-textarea2");
      
        if (multiMatch) {
          console.log("multiMatch found =>", multiMatch);
          console.log("Question =>", JSON.stringify(multiMatch[1]));
          console.log("Essay =>", JSON.stringify(multiMatch[2]));
      
          questionBox.value = multiMatch[1].trim();
          essayBox.value    = multiMatch[2].trim();
          return;
        }
      
        // Fallback approach:
        //  e.g. "** Question: **(some text up to newline) ... then '** Essay: **(remaining text)..."
        console.log("No multiMatch, trying fallback...");
        const qMatch = fullText.match(/\*\*\s*question:\s*\*\*(.*?)\n/i);
        const eMatch = fullText.match(/\*\*\s*essay:\s*\*\*(.*)/is);
      
        console.log("qMatch =>", qMatch);
        console.log("eMatch =>", eMatch);
      
        questionBox.value = qMatch ? qMatch[1].trim() : "";
        essayBox.value    = eMatch ? eMatch[1].trim() : "";
      }

    // For debugging, show text in #output
    function debugOutput(txt) {
        const outDiv = document.getElementById("output");
        if (outDiv) {
            outDiv.textContent = txt;
        }
    }

    // Send text to your API
    function sendTextToAPI(txt) {
        fetch("https://your-api-endpoint.com/analyze", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ question_text: txt, essay_text: txt })
        })
        .then(r => r.json())
        .then(data => {
            const feedbackDiv = document.getElementById("feedback");
            if (feedbackDiv) {
                feedbackDiv.innerHTML = `
                  <strong>Score:</strong> ${data.score}<br>
                  <strong>Feedback:</strong> ${data.feedback}
                `;
            }
        })
        .catch(err => {
            console.error("Error:", err);
            const feedbackDiv = document.getElementById("feedback");
            if (feedbackDiv) {
                feedbackDiv.textContent = "Error processing the request.";
            }
        });
    }

    // -----------------------------------------------------
    // Form Validation & Submission
    // -----------------------------------------------------
    document.querySelector(".desktop1-processbutton").addEventListener("click", function () {
        const email = document.querySelector(".desktop1-email input").value;
        if (!email.includes("@")) {
            alert("Please enter a valid email address.");
            return;
        }

        const question = document.querySelector(".desktop1-textarea3").value;
        const essay    = document.querySelector(".desktop1-textarea2").value;

        if (!question || !essay) {
            alert("Both Question and Essay fields must be filled.");
            return;
        }

        // Indicate processing in your .desktop1-text10
        document.querySelector(".desktop1-text10").textContent = "Processing...";

        // Example post to your back-end
        fetch("https://example.com/api/process", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, question, essay })
        })
        .then(r => r.json())
        .then(data => {
            document.querySelector(".desktop1-text10").textContent =
                data.reportLink || "Error processing request.";
        })
        .catch(() => {
            document.querySelector(".desktop1-text10").textContent =
                "Failed to process submission.";
        });
    });

    // Simple hover effect for all buttons
    document.querySelectorAll("button").forEach(button => {
        button.addEventListener("mouseover", () => {
            button.style.opacity = "0.8";
        });
        button.addEventListener("mouseout", () => {
            button.style.opacity = "1";
        });
    });
});