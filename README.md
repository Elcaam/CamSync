## CamSync
CamSync is a personal project for a browser based file management system that brings the familiarity of desktop
into a web-driven experience. It mimics SSD file manager systems directly in browser allowing the user
to upload and retrieve their files without relying on VM or external cloud services. So, the end goal is 
to try and build a smart, secure, and a privatefile manager that can combine the feel of SSD storage but with 
the fluidity of web app.

## Features
- Upload File(s)
- Instant search
- File Download
- Storage

## How it works
CamSync basically mimics the behavior of SSD storage at the application layer. 
Uploaded files are written to a dedicated folder on the server's filesystem and indexed on demand.
So, on each interaction, whether it's uploading, searching or whatnot, the app updates views and presents
a real-time data without requiring external databases or cloud services.

I built UI using standard HTML, CSS, and JS; Flask handles backend logic and file routing. Search queries are
handled on the server side and returned inro jinja templates to update UI accordingly.

## Technology:
Frontend: HTML, CSS, JS
Backend: Python, Flask
Templating: Jinja2
Search Logic: Keyword matching against filenames

## Features in progress
- File deletion
- Live filtering while typing

