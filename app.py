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

#what to do when a user selects index route
@app.route("/")
def home():
    """List all available API routes."""
    return(
        f"Welcome!<br>"
        f"Available routes:<br>"
        f"/api/v1.0/precipitation<br>"
        f"/api/v1.0/stations<br>"
        f"/api/v1.0/tobs<br>"
        f"/api/v1.0/2012.08.23<br>"
        f"/api/v1.0/2016.08.23/2016.09.05<br>"
        )

#what to do when user selects precipitation route
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

#what to do when user selects stations route
@app.route("/api/v1.0/stations")
def stations():
    """Return a list of stations from the dataset."""

    #query all stations from dataset
    results = session.query(station.station).all()

    #transform query results into a list
    all_stations = list(np.ravel(results))

    return jsonify(all_stations)

#what to do when user selects tobs route
@app.route("/api/v1.0/tobs")
def tobs():
    """Return a list of temperature observations for the the most active station for the previous year."""

    #calculating the date 1 year ago from the last data point in the database
    query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    #perform a query to retrieve the data and precipitation scores
    most_active = session.query(measurement.station, func.count(measurement.tobs)).\
        group_by(measurement.station).order_by(func.count(measurement.tobs).desc()).first()

    #pull just the station from the tuple
    most_active_station = most_active[0]

    #query for the max, min, and average temperature of the most active station
    session.query(measurement.station, func.max(measurement.tobs), func.min(measurement.tobs), func.avg(measurement.tobs)).\
        filter(measurement.station==most_active_station).all()

    #query the last 12 months of temperature observation data for this station
    tobs_query = session.query(measurement.tobs).filter(measurement.station==most_active_station).\
        filter(measurement.date>=query_date).all()

    return jsonify(tobs_query)

@app.route("/api/v1.0/2012.08.23")
def start(start_date=('2012-08-23')):
    """List of average, minimum, and maximum temperature for all dates greater than and equal to the start date."""

    temps_list = []

    #query the min, avg, and max temperature observations for all dates before and including the start date
    start_temps = session.query(measurement.date, func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start_date).all()

    #create a dict from the row data and append to list of temps_list
    for date, min, avg, max in start_temps:
        temps_dict = {}
        temps_dict['date'] = date
        temps_dict['tmin'] = min
        temps_dict['tavg'] = avg
        temps_dict['tmax'] = max
        temps_list.append(temps_dict)

    return jsonify(temps_list)

@app.route("/api/v1.0/2016.08.23/2016.09.05")
def calc_temps(start_date=('2016-08-23'), end_date=('2016-09-05')):
    """List of average, minimum, and maximum temperature for all dates inclusive of start and end date."""

    sec_temps_list = []

    #query the min, avg, and max temperature observations for all dates inclusive of the start and end dates
    temps = session.query(measurement.date, func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start_date).filter(measurement.date <= end_date).all()

    #create a dict from the row data and append to list of sec_temps_list
    for date, min, avg, max in temps:
        sec_temps_dict = {}
        sec_temps_dict['date'] = date
        sec_temps_dict['tmin'] = min
        sec_temps_dict['tavg'] = avg
        sec_temps_dict['tmax'] = max
        sec_temps_list.append(sec_temps_dict)

    return jsonify(sec_temps_list)

#close the session
session.close()

#run the app
if __name__ == "__main__":
    app.run(debug=True)