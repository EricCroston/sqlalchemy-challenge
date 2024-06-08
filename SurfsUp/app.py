# Import the dependencies.
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
station = Base.classes.station
measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(engine)


#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################
@app.route("/")
def homepage():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
	"""Return a dictionary using date and precipitation"""
	# Query only the last 12 months
	# Design a query to retrieve the last 12 months of precipitation data and plot the results. 
	# Starting from the most recent data point in the database. 
	most_recent = session.query(measurement).order_by(measurement.date.desc()).first()
	end_date = most_recent.date
	end_date = dt.datetime.strptime(end_date, '%Y-%m-%d')

	# Calculate the date one year from the last date in data set.
	start_date = end_date - dt.timedelta(days=365)
	end_date = end_date.strftime('%Y-%m-%d')
	start_date = start_date.strftime('%Y-%m-%d')

	# Perform a query to retrieve the data and precipitation scores
	last_twelve = session.query(measurement).\
		filter(measurement.date >= start_date).all()

	# Save the query results as a Pandas DataFrame. Explicitly set the column names
	last_twelve_result = [(x.date, x.prcp) for x in last_twelve]
	
	# Convert the list to a dictionary
	precipitation_dict = {date: prcp for date, prcp in last_twelve_result}
    
	# Return the dictionary as JSON
	return jsonify(precipitation_dict)

@app.route("/api/v1.0/stations")
def stations():
    """Return """
    # Query 
    stations = session.query(station).all()
    stations_list = [(x.station, x.name, x.latitude, x.longitude, x.elevation) for x in stations]

    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
    """Return """
    # Query 
    results = session.query(Passenger.name).all()

    

    # Convert list of tuples into normal list
    all_names = list(np.ravel(results))

    return jsonify(all_names)

# @app.route("/api/v1.0/<start>")
# def <start>():
#     """Return """
#     # Query 
#     results = session.query(Passenger.name).all()

    

#     # Convert list of tuples into normal list
#     all_names = list(np.ravel(results))

#     return jsonify(all_names)

# @app.route("/api/v1.0/<start>/<end>")
# def <start>/<end>():
#     """Return """
#     # Query 
#     results = session.query(Passenger.name).all()

    

#     # Convert list of tuples into normal list
#     all_names = list(np.ravel(results))

#     return jsonify(all_names)


# Close our session
session.close()

if __name__ == '__main__':
    app.run(debug=True)
