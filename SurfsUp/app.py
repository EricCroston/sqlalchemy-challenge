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
        f"/api/v1.0/<start> enter your start date YYYY-MM-DD<br/>"
        f"/api/v1.0/<start> enter your start date YYYY-MM-DD/<end> enter your end date YYYY-MM-DD"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
	"""Return a dictionary using date and precipitation"""
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

	# Save the query results into a list
	last_twelve_result = [(x.date, x.prcp) for x in last_twelve]
	
	# Convert the list to a dictionary
	precipitation_dict = {date: prcp for date, prcp in last_twelve_result}
    
	# Return the dictionary as JSON
	return jsonify(precipitation_dict)

@app.route("/api/v1.0/stations")
def stations():
    """Return a list of stations"""
    stations = session.query(station).all()
    stations_list = [(x.station, x.name, x.latitude, x.longitude, x.elevation) for x in stations]

    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
	# Design a query to find the most active stations (i.e. which stations have the most rows?)
	
	# List the stations and their counts in descending order.
	station_activity = session.query(measurement.station, func.count(measurement.station)).group_by(measurement.station).all()
	station_activity.sort(key=lambda x: x[1], reverse=True)
	
	# Starting from the most recent data point in the database. 
	most_recent = session.query(measurement).order_by(measurement.date.desc()).first()
	end_date = most_recent.date
	end_date = dt.datetime.strptime(end_date, '%Y-%m-%d')

	# Calculate the date one year from the last date in data set.
	start_date = end_date - dt.timedelta(days=365)
	end_date = end_date.strftime('%Y-%m-%d')
	start_date = start_date.strftime('%Y-%m-%d')

	# Using the most active station query the last 12 months of temperature observation data
	most_active = station_activity[0][0]
	most_active_py = session.query(measurement.tobs).\
		filter(measurement.station == most_active, 
			measurement.date >= start_date).all()

	# Save the query results into a list
	most_active_temps = [(x.tobs) for x in most_active_py]

    # Return the list as JSON
	return jsonify(most_active_temps)

@app.route("/api/v1.0/<start>")
def start(start):
	"""Return list of the minimum temperature, the average temperature and the 
	maximum temperature for the URL date"""

	# Set URL speified start date
	try:
		start_date = dt.datetime.strptime(start, '%Y-%m-%d')
		start_date = start_date.strftime('%Y-%m-%d')
	except ValueError:
		return jsonify({"error": "Incorrect date format, should be YYYY-MM-DD"}), 404


	# Design a query to calculate the lowest, average, and maximum temperature
	start_date_results = session.query(func.min(measurement.tobs),
										func.avg(measurement.tobs),
										func.max(measurement.tobs)).\
		filter(measurement.date == start_date).all()

	# Unpack the result tuple
	min_temp, avg_temp, max_temp = start_date_results[0]

	# Create a list to store the results
	temp_stats = [
		{"Start Date": start},
		{"Min Temperature": min_temp},
		{"Avg Temperature": avg_temp},
		{"Max Temperature": max_temp}
		]

	# Check that the Date is in the data
	if min_temp == None:
		return jsonify({"error": "Date not found."}), 404
	
	# Return the list as JSON
	return jsonify(temp_stats)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
	"""Return list of the minimum temperature, the average temperature and the 
	maximum temperature for the URL date range"""

# Set URL speified start date
	try:
		start_date = dt.datetime.strptime(start, '%Y-%m-%d')
		start_date = start_date.strftime('%Y-%m-%d')
	except ValueError:
		return jsonify({"error": "Incorrect start date format, should be YYYY-MM-DD"}), 404

	try:
		end_date = dt.datetime.strptime(end, '%Y-%m-%d')
		end_date = end_date.strftime('%Y-%m-%d')
	except ValueError:
		return jsonify({"error": "Incorrect end date format, should be YYYY-MM-DD"}), 404


	# Design a query to calculate the lowest, average, and maximum temperature
	date_range_results = session.query(func.min(measurement.tobs),
										func.avg(measurement.tobs),
										func.max(measurement.tobs)).\
		filter(measurement.date >= start_date, 
			measurement.date <= end_date).all()

	# Unpack the result tuple
	min_temp, avg_temp, max_temp = date_range_results[0]

	# Create a list to store the results
	temp_stats = [
		{"Start Date": start},
		{"End Date": end},
		{"Min Temperature": min_temp},
		{"Avg Temperature": avg_temp},
		{"Max Temperature": max_temp}
		]

	# Check that the Date is in the data
	if min_temp == None:
		return jsonify({"error": "Date not found."}), 404
	
	# Return the list as JSON
	return jsonify(temp_stats)


# Close our session
session.close()

if __name__ == '__main__':
    app.run(debug=True)
