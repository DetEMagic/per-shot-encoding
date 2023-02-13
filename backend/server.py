
# Importing flask module in the project is mandatory. An object of Flask class
# is our WSGI application.
import os
from flask import Flask, send_from_directory
from flask_cors import CORS

from api.routes.ScheduleAPI import schedule_api_routes
from api.scheduler.Job import create_job_table_db
from api.scheduler.VMAFDb import create_vmaf_db

# Create SQL tables.
create_job_table_db()
create_vmaf_db()

# Flask constructor takes the name of current module (__name__) as argument.
app = Flask(__name__, static_folder='../web-interface/build')
CORS(app)

# Register any imported blueprints
app.register_blueprint(schedule_api_routes, url_prefix="/api")


# Catch-all route that tries to serve static file if it exists, otherwise
# renders the react page in 'index.html'.
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_index(path):
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')


# Main driver function
if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
