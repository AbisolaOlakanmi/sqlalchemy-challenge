# Import the dependencies.

# Import dependencies.
from xml.sax.handler import DTDHandler
import matplotlib
from matplotlib import style
style.use('fivethirtyeight')
import matplotlib.pyplot as plt
import pandas as pd
import datetime as dt
import numpy as np

# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, inspect, func
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect an existing database into a new model

Base = automap_base()
Base.prepare(autoload_with=engine)
# reflect the tables

Base.classes.keys()

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
app = Flask(__name__)
#################################################

@app.route("/")
def welcome():
       """List all available routes."""
       return (
      f"Available Routes:<br/>"
      f"/api/v1.0/precipitation<br/>"
      f"/api/v1.0/stations<br/>"
      f"/api/v1.0/tobs<br/>"
      f"/api/v1.0/start<br/>"
      f"/api/v1.0/start/end<br/>")

# Convert the query results from your precipitation analysis (i.e. retrieve only the last 12 months of data) to a  dictionary using date as key and precipation as value

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    recent_date = DTDHandler.datetime(2017, 8, 23)

#"""Return a list of precipitation (prcp)and date (date) data"""


 # a new variable to store results from query to Measurement table for prcp and date columns
    precipitation_query_results = session.query(Measurement.prcp, Measurement.date).all()

    # Close session
    session.close()

#################################################
    precipitaton_query_values = []
    for prcp, date in precipitation_query_results:
        precipitation_dict = {}
        precipitation_dict["precipitation"] = prcp
        precipitation_dict["date"] = date
        precipitaton_query_values.append(precipitation_dict)

    return jsonify(precipitaton_query_values) 
# Flask Routes
###############################################
#station route
@app.route("/api/v1.0/stations")
def station():
     
     session = Session(engine)

    #  """Return a list of stations from the database""" 
     station_results = session.query(Station.station,Station.id).all()
     session.close()
     stations_list = []
     for station, id in station_results:
       stations_dict = {}
       stations_dict['station'] = station
       stations_dict['id'] = id
       stations_list.append(stations_dict)

       return jsonify(stations_list)
     
     ################################################   

#Query the dates and temperature of the most-active station for the previous year of data.
#tobs route

app.route("/api/v1.0/tobs")
def tobs():
      recent_date = dt.datetime(2017, 8, 23)
    # Calculating the date one year from the last date in data set.
query_date = dt.date(2017, 8, 23)-dt.timede(days = 365)
print(query_date)

session = Session(engine)
"""Return a list of dates and temps observed for the most active station for the last year of data from the database""" 
     #finding the most active station 
active_stat = session.query(Measurement.station, func.count(Measurement.station)).\
group_by(Measurement.station).order_by(func.count(Measurement.station).desc())
active_stations = active_stat.all()
most_active_stat = active_stat.first()[0]

session.close()
print(most_active_stat)

#the most active station id from the previous query

tobs_query= session.query(Measurement.date, Measurement.tobs, Measurement.station).\
        filter(Measurement.date > query_date).\
        filter(Measurement.station == most_active_stat) 
   #returning the list from the database
tobs_list = []
for date, tobs, in tobs_query:
    tobs_dict = {}
    tobs_dict['date'] = date
    tobs_dict['temperature'] = tobs
    tobs_list.append(tobs_dict)
    
return jsonify(tobs_dict) 

#start/end route

@app.route("/api/v1.0/<start>")
def start_date(start):
    session = Session(engine) 

    query_start=session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    
    session.close()

start_list= []
for min,max,avg in query_start:
        start_dict = {}
        start_dict['Min'] = min
        start_dict['Max'] = max
        start_dict['Average'] = avg
        start_list.append(start_dict)
        
        return jsonify(start_list)


#create an empty list to get all the key value pairs from the above query results by looping and appending the list

@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start,end):
    session = Session(engine)
    query_start_end = session.query(func.min(Measurements.tobs),\
                                func.max(Measurements.tobs),func.avg(Measurements.tobs)).\
                                filter(Measurements.date>=start).filter(Measurements.date<=end).all()
    session.close()
    start_end_list = []
    for min,max,avg in query_start_end:
        start_end_dict = {}
        start_end_dict['Min'] = min
        start_end_dict['Max'] = max
        start_end_dict['Average'] = avg
        start_end_list.append(start_end_dict)
    return jsonify(start_end_list)

if __name__ == '__main__':
    app.run(debug=True)


