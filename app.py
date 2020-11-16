#import dependencies
import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#database setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

#reflect an existing database into a new model
base = automap_base()

#reflect the tables
base.prepare(engine, reflect=True)

#save reference to the table
measurement = base.classes.measurement
station = base.classes.station

#create an app; flask setup
app = Flask(__name__)

#create one session (link) from python to the database for all routes
session = Session(engine)

#what to do when a user hits index route
@app.route("/")
def home():
    """List all available API routes."""
    return(
        f"Welcome!<br>"
        f"Available routes:<br>"
        f"/api/v1.0/precipitation<br>"
        f"/api/v1.0/stations<br>"
        f"/api/v1.0/tobs<br>"
        f"/api/v1.0/<start><br>"
        f"/api/v1.0/<start>/<end><br>"
        )

@app.route("/api/v1.0/precipitation")
def prcp():
    """Convert the query results to a dict using date as the key and prcp as the value."""

    #query all precipitation results
    query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    
    results = session.query(measurement.date, measurement.prcp).\
        filter(measurement.date >= query_date).all()


    #create a dict from the row data and append to list of prcp_list
    prcp_list = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict['date'] = date
        prcp_dict['prcp'] = prcp
        prcp_list.append(prcp_dict)

    return jsonify(prcp_list)
    
@app.route("/api/v1.0/stations")
def stations():
    """Return a list of stations from the dataset."""

    results = session.query(station.station).all()

    all_stations = list(np.ravel(results))

    return jsonify(all_stations)





#close the session
session.close()

#run the app
if __name__ == "__main__":
    app.run(debug=True)