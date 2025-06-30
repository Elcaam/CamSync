
"""
This web app wil basically allow users to upload files via a browser.
- After a file is uploaded, it will be saved temporarily and then encrypted using CamSync.exe.
- Encrypted files will be stored with a `.enc` extension in the 'uploads/' folder.
- Users see only the original filenames in the UI 
- When downloading, the app will decrypt the encrypted file on-demand and give it back under its original name.
"""



#Importing every file i need for the web to handle HTML rendering,
#routes, form request adn file sending as well.

from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
import subprocess

#Starting Flask app
app = Flask(__name__)

# Now, let's define the directory and the folder name to store the files which in this case
# will be 'uploads'

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# and then i have to make sire the upload folder exists brefore anything else
# if it does not, then create it
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# ----------------------------------------------------------------------
# Now, we will have the list of uploaded files but without .enc portion
# because the user don't really need to see that.
# ----------------------------------------------------------------------
@app.route('/')
def home():
    files = []

    # Check if upload directory exists
    if os.path.exists(app.config['UPLOAD_FOLDER']):
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            if filename.endswith('.enc'):
                # get rid of .enc so the user can only see the original filename
                display_name = filename[:-4]
                files.append(display_name)

    # Now let's render the main HTML template and pass in current file list
    return render_template('index.html', files=files)


# ---------------------------------------------------------------------------
# Let's handle some new file submissions. So, we check that the form 
# actually has a file to upload and make sure it supports multiple files
# in one upload. Then we save the uploaded files temporarily in plaintext 
# before we use CamSync.exe to encrypt it
# ---------------------------------------------------------------------------
@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return 'No file part in request.'

    files = request.files.getlist('file')

    for f in files:
        if f.filename != '':
            # Save to a temporary unencrypted path
            temp_path = os.path.join(app.config['UPLOAD_FOLDER'], f.filename)
            f.save(temp_path)

            # Defining the encrypted output path
            encrypted_path = os.path.join(app.config['UPLOAD_FOLDER'], f.filename + '.enc')

            # Calling CamSync.exe to encrypt 
            result = subprocess.run(
                ['CamSync.exe', 'encrypt', temp_path, encrypted_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            try:
                print("STDOUT:", result.stdout.decode('utf-8'))
            except UnicodeDecodeError:
                print("STDOUT (raw):", result.stdout)

            try:
                print("STDERR:", result.stderr.decode('utf-8'))
            except UnicodeDecodeError:
                print("STDERR (raw):", result.stderr)

            if result.returncode != 0:
                print("Encryption failed.")
                continue  #if encryption didn’t succeed, then 
                # we gotta skip deleting plaintext 

            # Remove unencrypted file
            os.remove(temp_path)

    return redirect(url_for('home'))

# ----------------------------------------------------------
#This is the search files portion. So, now we take 
# the search term from the form and convert it to lower
# matching cases and then look for files that contain search
# string in their name.
# ----------------------------------------------------------
@app.route('/search', methods=['POST'])
def search():
    # Get the search
    query = request.form.get('query', '').lower()
    results = []

    # Searching for filenames that contain the query string
    if os.path.exists(app.config['UPLOAD_FOLDER']):
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            if query in filename.lower():
                results.append(filename)

    # Reload all files
    files = os.listdir(app.config['UPLOAD_FOLDER']) if os.path.exists(app.config['UPLOAD_FOLDER']) else []
    return render_template('index.html', files=files, results=results)

# --------------------------------------------------------------------------
# For this portion, we Download and Decrypt the file(s).
# the route will handle when user tries to download the file
# and then after preparing the decrypted version of the file
# CamSync.exe will be ran and decrypted file will be sent back for download
# ---------------------------------------------------------------------------
@app.route('/uploads/<filename>')
def download_file(filename):
    # Append .enc to locate the encrypted file
    if not filename.endswith('.enc'):
        enc_file = os.path.join(app.config['UPLOAD_FOLDER'], filename + '.enc')
    else:
        enc_file = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    # remove .enc from the end if it's still there
    if filename.endswith('.enc'):
        output_filename = filename[:-4]
    else:
        output_filename = filename

    decrypted_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)

    subprocess.run([
        'CamSync.exe', 'decrypt', enc_file, decrypted_path
    ])

    # Serve decrypted file for download
    response = send_from_directory(
        app.config['UPLOAD_FOLDER'],
        output_filename,
        as_attachment=True
    )

    print("Decrypting:")
    print("Encrypted file path:", enc_file)
    print("Will write decrypted file to:", decrypted_path)

    return response


# ----------------------------------------------------
# ROUTE: Delete a user’s encrypted file
# ----------------------------------------------------
@app.route('/delete/<filename>', methods=['POST'])
def delete_file(filename):
    # All stored files end with .enc, even though the user doesn't see that
    encrypted_file = os.path.join(app.config['UPLOAD_FOLDER'], filename + '.enc')
    # Check if the file actually exists before trying to delete it
    if os.path.exists(encrypted_file):
        os.remove(encrypted_file)  # Remove the encrypted file from the server
        print(f"🗑️ Deleted file: {encrypted_file}")
    else:
        # If user somehow tries to delete a file that’s not there (e.g., typo or bug)
        print(f"⚠️ File not found for deletion: {encrypted_file}")

    # Redirect user back to the homepage after deletion
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
