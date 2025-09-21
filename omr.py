import os
import io
import json
from flask import Flask, render_template_string, request, redirect, url_for, send_from_directory
from PIL import Image, ImageOps
import numpy as np
from datetime import datetime

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

# Dummy answer keys: each subject 20 answers of A-D
ANSWER_KEYS = {
    'version1': {
        'subject1': ['A', 'B', 'C', 'D'] * 5,
        'subject2': ['D', 'C', 'B', 'A'] * 5,
        # Add more subjects if needed
    }
}

# Predefined bubble positions per subject (example: 20 questions * 4 options each)
# Coordinates: (x, y, width, height) - in pixels relative to resized image  (hardcoded example)
# You MUST adapt these coordinates to your actual sheet layout.
BUBBLE_POSITIONS = {
    'version1': {
        'subject1': [
            [(10+25*col, 20+30*row, 20, 20) for col in range(4)]
            for row in range(20)
        ],
        'subject2': [
            [(150+25*col, 20+30*row, 20, 20) for col in range(4)]
            for row in range(20)
        ]
    }
}

def preprocess_image(image: Image.Image) -> Image.Image:
    # Convert to grayscale
    gray = ImageOps.grayscale(image)
    # Resize to fixed width (e.g. 600px) for coordinate consistency
    wpercent = (600 / float(gray.size[0]))
    hsize = int((float(gray.size[1]) * float(wpercent)))
    gray = gray.resize((600, hsize))
    # Apply simple binary threshold
    bw = gray.point(lambda x: 0 if x > 128 else 255, '1')
    return bw

def detect_bubbles(image_bw: Image.Image, bubble_coords: list) -> list:
    # Returns list of selected answer ('A'-'D') or None per question
    img_np = np.array(image_bw, dtype=np.uint8)  # 0 or 255

    answers = []
    for question_bubbles in bubble_coords:
        fill_counts = []
        for (x,y,w,h) in question_bubbles:
            box = img_np[y:y+h, x:x+w]
            # Count black pixels (since bubbles marked are black areas)
            black_pixels = np.sum(box == 0)
            fill_counts.append(black_pixels)
        max_idx = np.argmax(fill_counts)
        max_val = fill_counts[max_idx]
        # Threshold for marked bubble (adjust as needed)
        if max_val > (0.5 *  w * h):
            answers.append(chr(ord('A') + max_idx))
        else:
            answers.append(None)  # no bubble detected or ambiguous
    return answers

def score_answers(extracted_ans: list, answer_key: list) -> int:
    score = 0
    for e,k in zip(extracted_ans, answer_key):
        if e == k:
            score += 1
    return score

@app.route('/', methods=['GET', 'POST'])
def upload_page():
    if request.method == 'POST':
        if 'sheet' not in request.files:
            return "No file uploaded", 400
        file = request.files['sheet']
        version = request.form.get('version', 'version1')

        if file.filename == '':
            return "No selected file", 400

        filename = datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + file.filename
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        # Process image
        orig_img = Image.open(filepath)
        bw_img = preprocess_image(orig_img)

        # Save processed image for audit trail
        proc_img_path = os.path.join(PROCESSED_FOLDER, f'proc_{filename}')
        bw_img.save(proc_img_path)

        # Evaluate each subject
        results = {}
        for subject, bubbles in BUBBLE_POSITIONS[version].items():
            extracted = detect_bubbles(bw_img, bubbles)
            key = ANSWER_KEYS[version][subject]
            score = score_answers(extracted, key)
            results[subject] = {
                'score': score,
                'answers': extracted
            }
        total = sum(r['score'] for r in results.values())

        # Save JSON audit
        audit = {
            'version': version,
            'results': results,
            'total': total,
            'processed_image': proc_img_path
        }
        audit_path = os.path.join(PROCESSED_FOLDER, f'result_{filename}.json')
        with open(audit_path, 'w') as f:
            json.dump(audit, f, indent=2)

        # Show results
        return render_template_string(TEMPLATE_RESULT,
                                      results=results,
                                      total=total,
                                      proc_img_url=url_for('processed_file', filename=os.path.basename(proc_img_path)))

    # GET method, show form
    return render_template_string(TEMPLATE_FORM)

@app.route('/processed/<path:filename>')
def processed_file(filename):
    return send_from_directory(PROCESSED_FOLDER, filename)

TEMPLATE_FORM = '''
<!doctype html>
<title>OMR Scanning System</title>
<h2>Upload OMR sheet photo</h2>
<form method=post enctype=multipart/form-data>
  <label>Choose exam version:</label>
  <select name="version">
    <option value="version1">Version 1</option>
  </select>
  <br><br>
  <input type=file name=sheet>
  <input type=submit value=Upload>
</form>
'''

TEMPLATE_RESULT = '''
<!doctype html>
<title>OMR Scan Results</title>
<h2>Result</h2>
<p><b>Total Score:</b> {{ total }}</p>
<table border=1 cellpadding=6>
  <thead><tr><th>Subject</th><th>Score (max 20)</th><th>Answers</th></tr></thead>
  <tbody>
    {% for subject, v in results.items() %}
      <tr>
        <td>{{ subject }}</td>
        <td>{{ v.score }}</td>
        <td>{{ v.answers|join(', ') }}</td>
      </tr>
    {% endfor %}
  </tbody>
</table>
<h3>Processed Image</h3>
<img src="{{ proc_img_url }}" style="max-width:600px; border:1px solid #ccc;">
<br><br>
<a href="/">Upload another sheet</a>
'''

if __name__ == '__main__':
    app.run(debug=True)