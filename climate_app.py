import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to the tables
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create session from Python to the Database
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

# last 12 months variable
year_ago = '2016-08-23'

# `/` Home page. List all routes that are available.
@app.route("/")
def index():
    return (
        f"Surf's up! Welcome to the Hawaii Weather API.<br/><br/>"
        f"/api/v1.0/precipitation<br/>Returns a JSON list of percipitation data for between 8/23/16 and 8/23/17<br/><br/>" 
        f"/api/v1.0/stations<br/>Returns a JSON list of the weather stations<br/><br/>"
        f"/api/v1.0/tobs<br/>Returns a JSON list of the Temperature Observations for each station between 8/23/16 and 8/23/17<br/><br/>"
        f"/api/v1.0/<start><br/>Returns a JSON list of the minimum temperature, max temperature, and average temperature between the given start date and 8/23/17<br/><br/>"
        f"/api/v1.0/<start>/<end><br/>Returns a JSON list of the minimum temperature, max temperature, and average temperature between the given start date and end date<br/><br/>"
    )

# * `/api/v1.0/precipitation`
#   * Convert the query results to a dictionary using `date` as the key and `prcp` as the value.
#   * Return the JSON representation of your dictionary.
# @app.route("/api/v1.0/precipitation")
# def precipitation():
#     precipitation_data = session.query(Measurement.date, func.avg(Measurement.prcp)).filter(Measurement.date >= year_ago).group_by(Measurement.date).all()
#     return jsonify(precipitation_data)

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    precipitation_data = session.query(Measurement.date, func.avg(Measurement.prcp)).\
        group_by(Measurement.date).all()
    session.close()
    rainfall_dates = []
    for date, prcp in precipitation_data:
        rainfall_dict = {}
        rainfall_dict["date"] = date
        rainfall_dict["prcp"] = prcp
        rainfall_dates.append(rainfall_dict)
    return jsonify(rainfall_dates)

# * `/api/v1.0/stations`
#   * Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    station_data = session.query(Station.station, Station.name).all()
    session.close()
    return jsonify(station_data)

# * `/api/v1.0/tobs`
#   * Query the dates and temperature observations of the most active station for the last year of data.
#   * Return a JSON list of temperature observations (TOBS) for the previous year.
@app.route("/api/v1.0/tobs")
def tobs():
    active_station_data = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == USC00519281).all()
    session.close()
    return jsonify(active_station_data)

# * `/api/v1.0/<start>` and `/api/v1.0/<start>/<end>`
#   * Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
#   * When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date.
#   * When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` for dates between the start and end date inclusive.
@app.route("/api/v1.0/<date>")
def startDateOnly(date):
    day_temp_data = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.date >= date).all()
    
    session.close()
    return jsonify(day_temp_data)

@app.route("/api/v1.0/<start>/<end>")
def startDateEndDate(start,end):
    multi_day_temp_data = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    session.close()
    return jsonify(multi_day_temp_data)

# Inputing "/api/v1.0/2016-08-27/2016-08-30" into my browser returns:
# 71.0, 81.0, 77.28... the min, max, and average over that 4-day period

if __name__ == "__main__":
    app.run(debug=True)