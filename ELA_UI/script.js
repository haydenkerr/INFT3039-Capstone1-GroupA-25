document.addEventListener("DOMContentLoaded", function () {

  // const host_port = "https://ielts-unisa-groupa.me"  
  //const host_port = "http://127.0.0.1:8008"    
  const host_port = "http://127.0.0.1:8001"      
      
  // const host_port = "http://3.24.180.235:8002"
  
    // Password protection for testing purposes
    // const password = "test123";
    // let enteredPassword = prompt("Enter password to access the site:");
    // if (enteredPassword !== password) {
    //     alert("Incorrect password. Access denied.");
    //     document.body.innerHTML = "<h2>Access Denied</h2>";
    //     return;
    // }

    //----------------------------------------
    // 1) WORD COUNT HELPER
    //----------------------------------------

    function updateWordCount() {
      const essayBox = document.querySelector("#essay-text");
      const wordCountInput = document.querySelector("#word-count");
      if (!essayBox || !wordCountInput) return;

      const text = essayBox.value.trim();
      // split on whitespace, filter empty strings
      const words = text ? text.split(/\s+/).filter(Boolean) : [];
      wordCountInput.value = words.length;
    }

    // Update wordcount whenever user types in the Essay
    document.querySelector("#essay-text")
      .addEventListener("keyup", updateWordCount);

    //----------------------------------------
    // 2) FILE UPLOAD
    //----------------------------------------
    document.querySelector(".file-upload button").addEventListener("click", () => {
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
      document.querySelector(".file-upload input[type='text']").value = file.name;
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
    // 3) INSERT TASK INSTRUCTIONS
    //----------------------------------------
    const taskInstructions = {
      "General Task 1": "You must respond to a situation by writing a letter, for example, asking for information or explaining a situation. You should write at least 150 words in about 20 minutes.",
      "General Task 2": "You must write an essay in response to a question. You should spend about 40 minutes on this task, and it is important that you write 250 words or more.",
      "Academic Task 1": "You must write an essay in response to data (in the form of a bar chart, line graph, pie chart or table), a process or map. You should write at least 150 words.",
      "Academic Task 2": "You must write an essay in response to a question. You should spend about 40 minutes on this task, and it is important that you write 250 words or more."
    };

    // Update instructions based on selected task type
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


    //----------------------------------------
    // 4) PARSE QUESTION/ESSAY
    //----------------------------------------
    function parseQuestionEssay(fullText) {
      // normalizing line breaks
      fullText = fullText.replace(/\r\n/g, "\n").replace(/\r/g, "\n");

      const questionBox = document.querySelector("#question-text");
      const essayBox    = document.querySelector("#essay-text");

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

  //--------------------------------------
  // 4) GET QUESTION BANK QUESTION
  //--------------------------------------

  const taskName = document.getElementById("task-type");
  const questionSelect = document.getElementById('generate-question');
  const questionText = document.getElementById('question-text');
  const essayText = document.getElementById('essay-text');

  questionSelect.addEventListener('change', function () {
    const selectedQuestion = questionSelect.value;
    const selectedTask = taskName.value;
    console.log('Selected Question Response:', selectedQuestion);
    console.log('Selected Task:', selectedTask);

    // Display error pop up if they try to ask for a question before selecting task  
    if (selectedQuestion == "Yes" && selectedTask == "Select an option") {
      alert("You must select a Task Type.");
      questionSelect.value = "Select an option"; // Set question drop down back to default
      return;
    }

    if (selectedQuestion == "Yes") {
      

  
      fetch(host_port + `/questions?task_name=${selectedTask}`, {
      method: "GET",
      headers: { "x-api-key": "1234abcd", "Content-Type": "application/json" },
      })
      .then(response => response.json())
      .then(data => {
      console.log("API response question:", data);

      const sampleQuestion = data.question;

      questionText.textContent = sampleQuestion;
      })

    } else {
      questionText.placeholder = "Upload a file, or enter your own question here";
      essayText.placeholder = "Upload a file, or enter your own essay here";
    }
  });  

//----------------------------------------
// 6) PROCESS SUBMISSION
//----------------------------------------
document.querySelector(".process-btn").addEventListener("click", function () {

  // Gather data from fields
  const email = document.querySelector("#email").value.trim();
  if (!email || !email.includes("@")) {
      alert("Please enter a valid email address.");
      return;
  }

  const question = document.querySelector("#question-text").value.trim();
  const essay    = document.querySelector("#essay-text").value.trim();
  if (!question || !essay) {
      alert("Both Question and Essay fields must be filled.");
      return;
  }

  const submissionGroup = document.querySelector("#submission-group").value;
  const taskType        = document.querySelector("#task-type").value;

  if (submissionGroup === "Select an option") {
    alert("You must select a Submission Group.");
    return;
  }

  if (taskType === "Select an option") {
    alert("You must select a Task Type.");
    return;
  }

  // read word count from input
  const wordCount = document.querySelector("#word-count").value || "0";

   const minWordCounts = {
    "General Task 1": 150,
    "General Task 2": 250,
    "Academic Task 1": 150,
    "Academic Task 2": 250
  }

  // Display confirm message if word count less than task minimum
  if (minWordCounts[taskType]) {
    const minCount = minWordCounts[taskType];
    const currentCount = parseInt(wordCount, 10);
    if (currentCount < minCount) {
      const proceed = confirm(`Are you sure you want to submit? The minimum word count for this task is ${minCount} words.`);
      if (!proceed) return;
    }
  }

  // Indicate we are "Processing"
  document.querySelector(".report-section").textContent = "Processing...";

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
  //   API call
  // -------------------------------------
  
  
  fetch(host_port + "/grade", {
    method: "POST",
    headers: { "x-api-key": "1234abcd", "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  })
  .then(response => response.json())
  .then(data => {
    console.log("API response data:", data);

    // Extract tracking_id and grading_result
    const trackingId = data.tracking_id;
    const gradingResult = data.grading_result;
    const overallScore = data.overall_score;

    console.log("Tracking ID:", trackingId);
    console.log("Grading Result:", gradingResult);
    console.log("Overall Score:", overallScore);

    // Update report section with tracking ID as a URL link and overall band.
    if (gradingResult && overallScore) {
      document.querySelector(".report-section").innerHTML =
      `<p><b>Submission Processed</b></p>
      <p>Overall Score: ${overallScore}</p>
      <p><a href="${host_port}/results/${trackingId}" target="_blank">Click here to view your full results</a></p>`;
    } else {
      document.querySelector(".report-section").innerHTML =
      `<p><b>Submission Processed</b></p>
      <p><a href="${host_port}/results/${trackingId}" target="_blank">Click here to view your full results</a></p>`;
    }
  })
  .catch(error => {
    console.error("API call error:", error);
    document.querySelector(".report-section").textContent =
      "Failed to process submission.";
  });
});


  //----------------------------------------
  // 7) HOVER EFFECTS
  //----------------------------------------
  document.querySelectorAll("button").forEach(button => {
    button.addEventListener("mouseover", () => {
      button.style.opacity = "0.8";
    });
    button.addEventListener("mouseout", () => {
      button.style.opacity = "1";
    });
  });
}
);