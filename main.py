import sys
from flask import Flask, request, render_template, jsonify
import sqlalchemy
from sqlalchemy.orm import declarative_base
from datetime import datetime


engine = sqlalchemy.create_engine("mariadb+mariadbconnector://rdessart:xxxx@localhost:3306/home")

Base = sqlalchemy.orm.declarative_base()

class HumidityValue(Base):
    __tablename__ = 'humidity'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    datetime = sqlalchemy.Column(sqlalchemy.DateTime)
    temperature = sqlalchemy.Column(sqlalchemy.Double)
    humidity = sqlalchemy.Column(sqlalchemy.Double)

    def Serialize(self):
        return {
            "Timestamp" : self.datetime.isoformat(),
            "Temperature": self.temperature,
            "Humidity": self.humidity,
        }

if(len(sys.argv) > 1):
    if(sys.argv[1] == "CREATE_DB"):
        Base.metadata.create_all(engine)

    elif(sys.argv[1] == "DROP_DB"):
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)


app = Flask(__name__)

Session = sqlalchemy.orm.sessionmaker()
Session.configure(bind=engine)
session = Session()

@app.route("/")
def hello_world():
    Session2 = sqlalchemy.orm.sessionmaker()
    Session2.configure(bind=engine)
    session = Session2()
    data = session.query(HumidityValue).all()
    data.reverse()
    return render_template("home.html", datas=data)

@app.route("/humidity/", methods=["GET"])
def getHumidity():
    Session2 = sqlalchemy.orm.sessionmaker()
    Session2.configure(bind=engine)
    session = Session2()
    data = session.query(HumidityValue).all()
    if(len(data) > 480):
        data = data[len(data)-28800:]
    return jsonify([d.Serialize() for d in data])

@app.route("/add/", methods=['POST'])
def postHumidity():
    temp = float(request.form['temperature'])
    humidity = float(request.form['humidity'])
    data = HumidityValue(
        datetime=datetime.now().isoformat(), 
        temperature=temp, 
        humidity=humidity)
    session.add(data)
    session.commit()
    return "<p>Received</p>"

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)