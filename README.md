hello we are the students of cananra engineering college a team of 3 varsha prathiksha and akshitha from mangalore. we have chossen the problem statement 1 
omr evaluation system.
# omr-eval

# OMR Sheet Evaluator 📝

A Flask-based web application that processes scanned/photographed OMR sheets, detects marked bubbles, and scores answers automatically using predefined answer keys.

---

## 🚀 Features
- Upload OMR sheet images and get them processed.
- Supports multiple **exam versions** and **subjects**.
- Auto-detects marked answers using bubble coordinates.
- Compares detected answers with answer keys and computes score.
- Provides a processed (binarized) image for verification.
- Saves results in JSON format for auditing.

---

## 🛠️ Tech Stack
- **Python 3.8+**
- **Flask** – web framework  
- **Pillow (PIL)** – image processing  
- **NumPy** – array operations  
- **HTML/CSS** – frontend templates  

---

## 📂 Project Structure


.
├── app.py # Main Flask app
├── uploads/ # Uploaded OMR sheets
├── processed/ # Processed images + results JSON
└── README.md # Project documentation


---

## ⚙️ Installation

1. **Clone the repo**
   ```bash
   git clone https://github.com/yourusername/omr-evaluator.git
   cd omr-evaluator


Create virtual environment (recommended)

python -m venv venv
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate      # Windows


Install dependencies

pip install -r requirements.txt


Example requirements.txt:

Flask
Pillow
numpy

▶️ Usage

Run the Flask app:

python app.py


Open your browser and go to:

http://127.0.0.1:5000/


Upload an OMR sheet image and select the exam version.

View:

Score per subject

Total score

Processed image

Answer extraction audit (JSON saved in processed/)

📊 Output Example

Processed Image (binarized & resized)

Results JSON:

{
  "version": "version1",
  "results": {
    "subject1": {
      "score": 85,
      "answers": ["A", "C", "B", "None", ...]
    }
  },
  "total": 85,
  "processed_image": "processed/proc_20250921_153012_sheet.jpg"
}

🔧 Configuration

Answer Keys are stored in ANSWER_KEYS dictionary.

Bubble positions auto-generated via BUBBLE_POSITIONS.

You can add new exam versions and subjects by extending these dictionaries.

🖼️ Demo

Upload an OMR sheet image.

Select the exam version.

Instantly get scores and processed results.

📜 License

MIT License – feel free to use and modify.
