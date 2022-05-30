import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
import datetime as dt

# database setup

engine = create_engine("sqlite:///Resources/hawaii.sqlite")



Base = automap_base()
Base.prepare(engine, reflect=True)

measurement = Base.classes.measurement
station = Base.classes.station

# setup Flask

app = Flask(__name__)

# route setup for flask

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    
    session = Session(engine)
    
    """Return a list of all precipitation data including date"""
    
    results = session.query(measurement.date,measurement.prcp).all()
    
    session.close()
    
    all_precipitation=[]
    for date,prcp in results:
        precipitation_dict = {}
        precipitation_dict[date] = prcp
        all_precipitation.append(precipitation_dict)
   
    return jsonify(all_precipitation)

@app.route("/api/v1.0/stations")
def station():
          
    session = Session(engine)
           
    """Return a list of all stations"""
           
    results = session.query(measurement.station).group_by(measurement.station).all()
    session.close()
    stations = list(np.ravel(results))
   
    return jsonify(stations=stations)
           
           
@app.route("/api/v1.0/tobs")
def tobs():

    session = Session(engine)
           
    """Return a list of temperature observation data including date"""
    temperature_date = session.query(measurement.date).order_by(measurement.date.desc()).first()       
    recent_temp_date = list(np.ravel(temperature_date))[0]
    format_temp_date = dt.datetime.strptime(recent_temp_date,"%Y-%m-%d")

    one_year = format_temp_date-dt.timedelta(days=365)
    
    results = session.query(measurement.date,measurement.tobs).order_by(measurement.date.desc()).filter(measurement.date>=one_year).all()
    session.close()
    all_temperatures=[]
    for date,tobs in results:
        tobs_dict={}
        tobs_dict['date']=date
        tobs_dict['tobs']=tobs
        all_temperatures.append(tobs_dict)
    return jsonify(all_temperatures)

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def temperature_calculations():
    session = Session(engine)
 
    """TMIN, TAVG, & TMAX for dates"""
    sel = [func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)] 
    if not end:
        results = session.query(*sel).filter(measurement.date >= start).all()                
        temp_stats = list(np.ravel(results))
        return jsonify(temp_stats=temp_stats)
           

    results = session.query(*sel).filter(measurement.date >= start).filter(measurement.date <= end).all() 
    stats_end = list(np.ravel(results))
   
    return jsonify(stats_end=stats_end)
if __name__ == '__main__':
    app.run(debug=True)
           
    
           
    
   
        
        