# MSME Guide

## Run the website

Install Python 3.10 or newer, then open a terminal in this folder and run:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python main.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000). The database is created in
`Flask-Web-App-Tutorial-main/instance/database.db` the first time the app starts.
You can browse the MSME pages without an account. Create an account to register a
business and view your registration confirmation.

Set the `SECRET_KEY` environment variable to a private random value before
deploying this site anywhere beyond local development.

## Publish the source and deploy the live Flask site

GitHub Pages only hosts static files, so it cannot run this app's Flask routes,
sign-in, or business registration database. The repository includes a Render
Blueprint for the Flask web service. The first Render setup also needs a
persistent PostgreSQL `DATABASE_URL`; do not use the local SQLite file in a
hosted service because hosted filesystems can be temporary.

1. Create a **public** GitHub repository and push this project to its `main`
   branch.
2. Create a PostgreSQL database with a provider such as Neon, and copy its
   connection URL. Keep that URL private.
3. In Render, choose **New → Blueprint**, connect the GitHub repository, and
   set the prompted `DATABASE_URL` to the PostgreSQL connection URL. The
   Blueprint generates `SECRET_KEY` and configures the web service.
4. When the deploy completes, open the `onrender.com` URL shown in Render.

The free Render web service can sleep when idle; the app wakes when someone
opens it. Keep the database URL private and never commit it to GitHub.
