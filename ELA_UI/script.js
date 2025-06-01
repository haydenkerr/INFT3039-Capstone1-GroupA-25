document.addEventListener("DOMContentLoaded", function () {
  // Wait for config.js async check to finish before using HOST_PORT/API_KEY
  if (!window.APP_CONFIG_READY) {
    console.error("APP_CONFIG_READY is not defined. Make sure config.js is loaded before script.js.");
    return;
  }
  window.APP_CONFIG_READY.then(() => {
    const HOST_PORT = window.APP_CONFIG ? window.APP_CONFIG.HOST_PORT : "";
    const API_KEY = window.APP_CONFIG ? window.APP_CONFIG.API_KEY : "";

    // 1) WORD COUNT HELPER
    function updateWordCount() {
      const essayBox = document.querySelector("#essay-text");
      const wordCountInput = document.querySelector("#word-count");
      if (!essayBox || !wordCountInput) return;
      const text = essayBox.value.trim();
      const words = text ? text.split(/\s+/).filter(Boolean) : [];
      wordCountInput.value = words.length;
    }
    document.querySelector("#essay-text").addEventListener("keyup", updateWordCount);

    // 2) FILE UPLOAD
    document.querySelector(".file-upload button").addEventListener("click", () => {
      document.getElementById("fileInput").click();
      
    });
    document.getElementById("fileInput").addEventListener("change", handleFile);
    document.getElementById("pdf-format-warning").style.display = "none";

    function sanitizeMammothOutput(htmlString) {
      const tempDiv = document.createElement("div");
      tempDiv.innerHTML = htmlString;
      const textLines = [];
      tempDiv.childNodes.forEach(node => {
        if (node.nodeName === "P") {
          const line = node.textContent.trim();
          if (line !== "") textLines.push(line);
        } else if (node.nodeName === "UL" || node.nodeName === "OL") {
          const items = node.querySelectorAll("li");
          items.forEach(li => {
            const bullet = node.nodeName === "OL" ? `${textLines.length + 1}. ` : "• ";
            textLines.push(bullet + li.textContent.trim());
          });
        }
      });
      return textLines.join("\n\n");
    }

    function handleFile(e) {
      const file = e.target.files[0];
      if (!file) {
        alert("Please select a file.");
        return;
      }
      document.querySelector(".file-upload input[type='text']").value = file.name;
      const extension = file.name.toLowerCase().split(".").pop();
      document.getElementById("pdf-format-warning").style.display = "none";
      document.getElementById("docx-format-warning").style.display = "none";
      document.getElementById("txt-format-warning").style.display = "none";

      if (extension === "txt") {
        document.getElementById("txt-format-warning").style.display = "block";
        const reader = new FileReader();
        reader.onload = function(ev) {
          const text = ev.target.result;
          parseQuestionEssay(text);
          updateWordCount();
        };
        reader.readAsText(file);
      } else if (extension === "docx") {
        document.getElementById("docx-format-warning").style.display = "block";
        const reader = new FileReader();
        reader.onload = function() {
          mammoth.convertToHtml({ arrayBuffer: reader.result })
            .then(result => {
              const cleanedText = sanitizeMammothOutput(result.value);
              parseQuestionEssay(cleanedText);
              updateWordCount();
            })
            .catch(err => {
              console.error("Error processing DOCX:", err);
            });
        };
        reader.readAsArrayBuffer(file);
      } else if (extension === "pdf") {
        document.getElementById("pdf-format-warning").style.display = "block";
        const reader = new FileReader();
        reader.onload = function () {
          const base64 = reader.result.split(',')[1];
          fetch(`${HOST_PORT}/extract-pdf-text`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ file: base64 })
          })
            .then(res => res.json())
            .then(data => {
              parseQuestionEssay(data.text);
              updateWordCount();
            })
            .catch(err => {
              console.error("PDF processing failed:", err);
              alert("There was an error extracting text from the PDF.");
            });
        };
        reader.readAsDataURL(file);
      } else {
        alert("Unsupported file format. Please upload a TXT, PDF, or DOCX file.");
      }
    }

    // 3) INSERT TASK INSTRUCTIONS
    const taskInstructions = {
      "General Task 1": "You must respond to a situation by writing a letter, for example, asking for information or explaining a situation. You should write at least 150 words in about 20 minutes.",
      "General Task 2": "You must write an essay in response to a question. You should spend about 40 minutes on this task, and it is important that you write 250 words or more.",
      "Academic Task 1": "You must write an essay in response to data (in the form of a bar chart, line graph, pie chart or table), a process or map. You should write at least 150 words.",
      "Academic Task 2": "You must write an essay in response to a question. You should spend about 40 minutes on this task, and it is important that you write 250 words or more."
    };
    const taskTypeSelect = document.getElementById('task-type');
    const instructionsText = document.getElementById('instructions-text');
    taskTypeSelect.addEventListener('change', function () {
      const selectedTask = taskTypeSelect.value;
      console.log('Selected Task:', selectedTask);
      if (taskInstructions[selectedTask]) {
        instructionsText.textContent = taskInstructions[selectedTask];
      } else {
        instructionsText.textContent = "Select a task type to view the instructions.";
      }
    });

    // 4) PARSE QUESTION/ESSAY
    function parseQuestionEssay(fullText) {
      fullText = fullText.replace(/\r\n/g, "\n").replace(/\r/g, "\n");
      const questionBox = document.querySelector("#question-text");
      const essayBox = document.querySelector("#essay-text");
      const multiRegex = /\*\*\s*question:\s*\*\*([\s\S]+?)\*\*\s*essay:\s*\*{2}([\s\S]+)/i;
      const multiMatch = fullText.match(multiRegex);
      if (multiMatch) {
        questionBox.value = multiMatch[1].trim();
        essayBox.value = multiMatch[2].trim();
        return;
      }
      const qMatch = fullText.match(/\*\*\s*question:\s*\*\*(.*?)\n/i);
      const eMatch = fullText.match(/\*\*\s*essay:\s*\*\*(.*)/is);
      questionBox.value = qMatch ? qMatch[1].trim() : "";
      essayBox.value = eMatch ? eMatch[1].trim() : "";
    }

    // 5) GET QUESTION BANK QUESTION
    const taskName = document.getElementById("task-type");
    const questionSelect = document.getElementById('generate-question');
    const questionText = document.getElementById('question-text');
    const essayText = document.getElementById('essay-text');
    questionSelect.addEventListener('change', function () {
      const selectedQuestion = questionSelect.value;
      const selectedTask = taskName.value;
      if (selectedQuestion == "Yes" && selectedTask == "Select an option") {
        alert("You must select a Task Type.");
        questionSelect.value = "Select an option";
        return;
      }
      if (selectedQuestion == "Yes") {
        fetch(HOST_PORT + `/questions?task_name=${selectedTask}`, {
          method: "GET",
          headers: { "x-api-key": API_KEY, "Content-Type": "application/json" },
        })
          .then(response => response.json())
          .then(data => {
            console.log("API response question:", data);
            const sampleQuestion = data.question;
            questionText.value = sampleQuestion;
          });
      } else {
        questionText.placeholder = "Upload a file, or enter your own question here";
        essayText.placeholder = "Upload a file, or enter your own essay here";
      }
    });

    // 6) PROCESS SUBMISSION
    document.querySelector(".process-btn").addEventListener("click", function () {
      const email = document.querySelector("#email").value.trim();
      if (!email || !email.includes("@")) {
        alert("Please enter a valid email address.");
        return;
      }
      const question = document.querySelector("#question-text").value.trim();
      const essay = document.querySelector("#essay-text").value.trim();
      if (!question || !essay) {
        alert("Both Question and Essay fields must be filled.");
        return;
      }
      const submissionGroup = document.querySelector("#submission-group").value;
      const taskType = document.querySelector("#task-type").value;
      if (submissionGroup === "Select an option") {
        alert("You must select a Submission Group.");
        return;
      }
      if (taskType === "Select an option") {
        alert("You must select a Task Type.");
        return;
      }
      const wordCount = document.querySelector("#word-count").value || "0";
      const minWordCounts = {
        "General Task 1": 150, //1
        "General Task 2": 250, //2
        "Academic Task 1": 150, //3
        "Academic Task 2": 250 //4
      };
      if (minWordCounts[taskType]) {
        const minCount = minWordCounts[taskType];
        const currentCount = parseInt(wordCount, 10);
        if (currentCount < minCount) {
          const proceed = confirm(`Are you sure you want to submit? The minimum word count for this task is ${minCount} words.`);
          if (!proceed) return;
        }
      }
      document.querySelector(".report-section").textContent = "Processing...";
      const payload = {
        email,
        question,
        essay,
        wordCount,
        submissionGroup,
        taskType
      };
      fetch(HOST_PORT + "/grade", {
        method: "POST",
        headers: { "x-api-key": API_KEY, "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      })
        .then(response => response.json())
        .then(data => {
          console.log("API response data:", data);
          const trackingId = data.tracking_id;
          const gradingResult = data.grading_result;
          const overallScore = data.overall_score;

          console.log("Tracking ID:", trackingId);
          console.log("Grading Result:", gradingResult);
          console.log("Overall Score:", overallScore);
          if (gradingResult && overallScore) {
            document.querySelector(".report-section").innerHTML =
              `<p><b>Submission Processed</b></p>
              <p>Overall Score: ${overallScore}</p>
              <p><a href="${HOST_PORT}/results/${trackingId}" target="_blank">Click here to view your full results</a></p>`;
          } else {
            document.querySelector(".report-section").innerHTML =
              `<p><b>Submission Processed</b></p>
              <p><a href="${HOST_PORT}/results/${trackingId}" target="_blank">Click here to view your full results</a></p>`;
          }
        })
        .catch(error => {
          console.error("API call error:", error);
          document.querySelector(".report-section").textContent =
            "Failed to process submission.";
        });
    });

    // 7) HOVER EFFECTS
    document.querySelectorAll("button").forEach(button => {
      button.addEventListener("mouseover", () => {
        button.style.opacity = "0.8";
      });
      button.addEventListener("mouseout", () => {
        button.style.opacity = "1";
      });
    });

    // View My Previous Submissions button handler
    document.getElementById('view-submissions-btn').onclick = function() {
      const email = document.getElementById('email').value.trim();
      if (!email) {
        alert("Please enter your email address first.");
        return;
      }
      window.open(HOST_PORT + `/submissions/${encodeURIComponent(email)}`, '_blank');
    };

    document.getElementById("clear-upload").addEventListener("click", () => {
      document.getElementById("fileInput").value = "";
      document.querySelector("#question-text").value = "";
      document.querySelector("#essay-text").value = "";
      document.querySelector("#word-count").value = "";
      document.querySelector(".file-upload input[type='text']").value = "";
      document.getElementById("pdf-format-warning").style.display = "none";
      document.getElementById("docx-format-warning").style.display = "none";
      document.getElementById("txt-format-warning").style.display = "none";
      // Reset the "Generate Question" dropdown to default so it can be used again
      document.getElementById("generate-question").value = "Select an option";
      // Optionally reset placeholders
      document.querySelector("#question-text").placeholder = "Upload a file, or enter your own question here";
      document.querySelector("#essay-text").placeholder = "Upload a file, or enter your own essay here";
    });
  });
});