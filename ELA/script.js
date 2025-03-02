document.addEventListener("DOMContentLoaded", function () {

    //----------------------------------------
    // 1) WORD COUNT HELPER
    //----------------------------------------
    function updateWordCount() {
      const essayBox = document.querySelector(".desktop1-textarea2");
      const wordCountInput = document.querySelector(".desktop1-wordcount input");
      if (!essayBox || !wordCountInput) return;

      const text = essayBox.value.trim();
      // split on whitespace, filter empty strings
      const words = text ? text.split(/\s+/).filter(Boolean) : [];
      wordCountInput.value = words.length;
    }

    // Update wordcount whenever user types in the Essay
    document.querySelector(".desktop1-textarea2")
      .addEventListener("keyup", updateWordCount);

    //----------------------------------------
    // 2) FILE UPLOAD
    //----------------------------------------
    document.querySelector(".desktop1-uploadfilebutton").addEventListener("click", () => {
        document.getElementById("fileInput").click();
    });

    document.getElementById("fileInput").addEventListener("change", handleFile);

    function handleFile(e) {
      const file = e.target.files[0];
      if (!file) {
        alert("Please select a file.");
        return;
      }

      // show filename
      document.querySelector(".desktop1-input2").value = file.name;
      const extension = file.name.toLowerCase().split(".").pop();

      if (extension === "txt") {
        // parse text file
        const reader = new FileReader();
        reader.onload = function(ev) {
          const text = ev.target.result;
          parseQuestionEssay(text);
          updateWordCount(); // update word count now that essay may be filled
        };
        reader.readAsText(file);
      }
      else if (extension === "docx") {
        // parse docx using mammoth
        const reader = new FileReader();
        reader.onload = function() {
          mammoth.extractRawText({ arrayBuffer: reader.result })
            .then(result => {
              const docxText = result.value;
              parseQuestionEssay(docxText);
              updateWordCount();
            })
            .catch(err => {
              console.error("Error processing DOCX:", err);
            });
        };
        reader.readAsArrayBuffer(file);
      }
      else if (extension === "pdf") {
        // parse pdf using pdf.js
        const reader = new FileReader();
        reader.onload = function() {
          const typedarray = new Uint8Array(reader.result);
          extractTextFromPDF(typedarray)
            .then(pdfText => {
              parseQuestionEssay(pdfText);
              updateWordCount();
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

    // pdf.js extraction
    function extractTextFromPDF(typedarray) {
      return pdfjsLib.getDocument(typedarray).promise.then(pdf => {
        let text = "";
        const promises = [];
        for (let i = 1; i <= pdf.numPages; i++) {
          promises.push(
            pdf.getPage(i).then(page =>
              page.getTextContent().then(tc => {
                const pageText = tc.items.map(item => item.str).join(" ");
                text += pageText + "\n";
              })
            )
          );
        }
        return Promise.all(promises).then(() => text);
      });
    }

    //----------------------------------------
    // 3) PARSE QUESTION/ESSAY
    //----------------------------------------
    function parseQuestionEssay(fullText) {
      // normalizing line breaks
      fullText = fullText.replace(/\r\n/g, "\n").replace(/\r/g, "\n");

      const questionBox = document.querySelector(".desktop1-textarea3");
      const essayBox    = document.querySelector(".desktop1-textarea2");

      // Attempt a multiline capture:
      const multiRegex = /\*\*\s*question:\s*\*\*([\s\S]+?)\*\*\s*essay:\s*\*\*([\s\S]+)/i;
      const multiMatch = fullText.match(multiRegex);
      if (multiMatch) {
        questionBox.value = multiMatch[1].trim();
        essayBox.value    = multiMatch[2].trim();
        return;
      }

      // fallback approach
      const qMatch = fullText.match(/\*\*\s*question:\s*\*\*(.*?)\n/i);
      const eMatch = fullText.match(/\*\*\s*essay:\s*\*\*(.*)/is);

      questionBox.value = qMatch ? qMatch[1].trim() : "";
      essayBox.value    = eMatch ? eMatch[1].trim() : "";
    }

    //----------------------------------------
    // 4) PROCESS SUBMISSION
    //----------------------------------------
    document.querySelector(".desktop1-processbutton").addEventListener("click", function () {

        // Gather data from fields
        const email = document.querySelector(".desktop1-email input").value.trim();
        if (!email || !email.includes("@")) {
            alert("Please enter a valid email address.");
            return;
        }

        const question = document.querySelector(".desktop1-textarea3").value.trim();
        const essay    = document.querySelector(".desktop1-textarea2").value.trim();
        if (!question || !essay) {
            alert("Both Question and Essay fields must be filled.");
            return;
        }

        // read word count from input
        const wordCount = document.querySelector(".desktop1-wordcount input").value || "0";

        const submissionGroup = document.querySelector(".desktop1-submissiongroup select").value;
        const taskType        = document.querySelector(".desktop1-tasktype select").value;

        // Indicate we are "Processing"
        document.querySelector(".desktop1-text10").textContent = "Processing...";

        // Build a JSON payload
        const payload = {
          email,
          question,
          essay,
          wordCount,
          submissionGroup,
          taskType
        };

        console.log("[Process Submission] Payload:", payload);

        // -------------------------------------
        //  OPTIONAL: API call commented out
        // -------------------------------------
        /*
        fetch("https://your-api-endpoint.com/analyze", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        })
        .then(response => response.json())
        .then(data => {
          console.log("API response data:", data);
          document.querySelector(".desktop1-text10").textContent =
            data.reportLink || "Request processed. See console for details.";
        })
        .catch(error => {
          console.error("API call error:", error);
          document.querySelector(".desktop1-text10").textContent =
            "Failed to process submission.";
        });
        */

        // For now, just indicate done
        document.querySelector(".desktop1-text10").textContent =
          "Submission processed (no live API call).";
    });

    //----------------------------------------
    // 5) HOVER EFFECTS
    //----------------------------------------
    document.querySelectorAll("button").forEach(button => {
      button.addEventListener("mouseover", () => {
        button.style.opacity = "0.8";
      });
      button.addEventListener("mouseout", () => {
        button.style.opacity = "1";
      });
    });
});
