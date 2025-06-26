# Importing the necessary Flask components and Python modules
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os

#Flask app
app = Flask(__name__)

# Below, i'm defininf the directory where uploaded files will be stored
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# and then i have to make sire the upload folder exists...if not, create it
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# ----------------------------------------------
# Loading the main UI with file list
# ----------------------------------------------
@app.route('/')
def home():
    files = []

    # we gotta check if upload directory exists and then collect filenames
    if os.path.exists(app.config['UPLOAD_FOLDER']):
        files = os.listdir(app.config['UPLOAD_FOLDER'])

    # Now let's Render the main HTML template and pass in current file list
    return render_template('FileRetrieval.html', files=files)

# ------------------------------------------------
# Let's handle some new file submissions
# ------------------------------------------------
@app.route('/upload', methods=['POST'])
def upload():
    # just Making sure a file was submitted in the form
    if 'file' not in request.files:
        return 'No file part in request.'

    files = request.files.getlist('file')

    for f in files:
        # just ignore empty filenames
        if f.filename != '':
            #Path for saving the file
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], f.filename)
            # Save to disk
            f.save(save_path)

    # Go back to the homepage
    return redirect(url_for('home'))

# ----------------------------------------------------------
# keyword search portion
# ----------------------------------------------------------
@app.route('/search', methods=['POST'])
def search():
    # Get the search query 
    query = request.form.get('query', '').lower()
    results = []

    # Searching for filenames that contain the query string
    if os.path.exists(app.config['UPLOAD_FOLDER']):
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            if query in filename.lower():
                results.append(filename)

    # Reload all files
    files = os.listdir(app.config['UPLOAD_FOLDER']) if os.path.exists(app.config['UPLOAD_FOLDER']) else []
    return render_template('FileRetrieval.html', files=files, results=results)

# ----------------------------------------------------
# FILE DOWNLOAD PORTION
# ----------------------------------------------------
@app.route('/uploads/<filename>')
def download_file(filename):
    # SendING the requested file from the upload directory as an attachment
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

# -------------------------
# Launch the Flask server
# -------------------------
if __name__ == '__main__':
    app.run(debug=True)
