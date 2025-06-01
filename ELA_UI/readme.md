# 📘 ELA - English Language Assistant Pro

This project provides a browser-based interface for uploading and submitting IELTS-style questions and essays for automated evaluation. It leverages a local or network-hosted API backend for grading.

---

## 🔧 Prerequisites
- A modern web browser (Chrome, Firefox, Edge)
- Optional: A running API backend listening on the endpoint defined in `script.js` (default: `http://192.168.1.17:8001/grade`)

---

## 🚀 How to Run the App

1. **Clone or Download** this repository locally.
2. Make sure these files are in the same directory:
   - `index.html`
   - `script.js`
   - `style.css`
3. Simply open `index.html` in your web browser by:
   - Double-clicking the file **or**
   - Right-click > Open with > your preferred browser

That's it! No additional build steps required. This is a fully client-side HTML/CSS/JS application.


---

## 📁 Features
- Upload essays and questions from `.txt`, `.pdf`, or `.docx` files
- Auto-fill question and essay fields from uploaded file
- Real-time word count tracking
- Submit essay/question to an API endpoint for evaluation
- Downloadable essay template

---

## 🔒 Security Notes
- 
- For production, consider securing API access using environment variables or server-side authentication.

---

## 📤 Submitting Essays
To test submission:
- Enter your email
- Fill in question and essay fields manually **or** upload a `.txt`, `.docx`, or `.pdf` file
- Click **Process Submission**

The system will display a loading message and update with a report link or status when processing is complete.

---

## 📎 Example File Format
```
** question: **
Your IELTS writing prompt here

** essay: **
Your essay response here
```
You can download the sample template provided in the interface for reference.

---

## 🛠 Optional Backend API
To enable live grading:
- Make sure the FastAPI backend is running and accessible
- Endpoint: `http://<your-ip>:8001/grade`
- Ensure CORS and API key are correctly configured (see `main.py`)

---

## 💬 Feedback
For bug reports or feature requests, please open an issue in the repository or contact the developer team.

Enjoy using ELA! 🎓
