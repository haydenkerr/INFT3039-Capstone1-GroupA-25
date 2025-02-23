document.getElementById('fileInput').addEventListener('change', handleFile);

function handleFile(event) {
    const file = event.target.files[0];
    if (!file) {
        alert("Please select a file.");
        return;
    }
    const reader = new FileReader();

    if (file.name.endsWith('.docx')) {
        reader.readAsArrayBuffer(file);
        reader.onload = function(event) {
            const arrayBuffer = reader.result;
            mammoth.extractRawText({ arrayBuffer: arrayBuffer })
                .then(function(result) {
                    displayText(result.value);
                    sendTextToAPI(result.value);
                })
                .catch(function(err) {
                    console.error("Error processing DOCX: ", err);
                });
        };
    } else if (file.name.endsWith('.pdf')) {
        reader.readAsArrayBuffer(file);
        reader.onload = function(event) {
            const typedarray = new Uint8Array(reader.result);
            extractTextFromPDF(typedarray);
        };
    } else {
        alert("Unsupported file format. Please upload a PDF or DOCX.");
    }
}

function extractTextFromPDF(typedarray) {
    pdfjsLib.getDocument(typedarray).promise.then(pdf => {
        let text = "";
        const maxPages = pdf.numPages;
        let countPromises = [];
        for (let i = 1; i <= maxPages; i++) {
            countPromises.push(pdf.getPage(i).then(page => {
                return page.getTextContent().then(textContent => {
                    let pageText = textContent.items.map(item => item.str).join(" ");
                    text += pageText + "\n";
                });
            }));
        }
        return Promise.all(countPromises).then(() => {
            displayText(text);
            sendTextToAPI(text);
        });
    }).catch(error => {
        console.error("Error processing PDF: ", error);
    });
}

function displayText(text) {
    document.getElementById("output").innerText = text;
}

function sendTextToAPI(text) {
    fetch('https://your-api-endpoint.com/analyze', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ essay_text: text })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById("feedback").innerHTML = `<strong>Score:</strong> ${data.score}<br><strong>Feedback:</strong> ${data.feedback}`;
    })
    .catch(error => {
        console.error("Error:", error);
        document.getElementById("feedback").innerText = "Error processing the request.";
    });
}
