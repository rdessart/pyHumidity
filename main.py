import sys
from flask import Flask, request, render_template, jsonify, Response
import sqlalchemy
from sqlalchemy.orm import declarative_base
from datetime import datetime
from openpyxl import Workbook
from flask_sock import Sock
from flask_socketio import SocketIO



engine = sqlalchemy.create_engine("mariadb+mariadbconnector://rdessart:roro3323@192.168.0.10:3306/home")

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
app.config['SECRET_KEY'] = 'secret!'
app.config['DEBUG'] = True
app.config['TESTING'] = True
socketio = SocketIO(app)

Session = sqlalchemy.orm.sessionmaker()
Session.configure(bind=engine)
session = Session()

@app.route("/")
def hello_world():
    Session2 = sqlalchemy.orm.sessionmaker()
    Session2.configure(bind=engine)
    session = Session2()
    data = session.query(HumidityValue).all()
    if len(data) > 500:
        data = data[len(data)-500:]
    data.reverse()
    return render_template("home.html", datas=data)


@app.route("/humidity/<maxVal>", methods=["GET"])
def getHumidity(maxVal=-1):
    maxVal = int(maxVal)
    Session2 = sqlalchemy.orm.sessionmaker()
    Session2.configure(bind=engine)
    session = Session2()
    data = session.query(HumidityValue).all()
    if maxVal < 0:
        return jsonify([d.Serialize() for d in data])
    if(len(data) > maxVal):
        data = data[len(data) - maxVal:]
    return jsonify([d.Serialize() for d in data])


@app.route("/add/", methods=['POST'])
def postHumidity():
    temp = float(request.form['temperature'])
    humidity = float(request.form['humidity'])
    data = HumidityValue(
        datetime=datetime.now().isoformat(), 
        temperature=temp, 
        humidity=humidity)
    # session.add(data)
    # session.commit()
    socketio.emit('newHumidity', data, broadcast=True)
    return "<p>Received</p>"


@app.route("/get_csv/", methods=['GET'])
def getHumidityCSV():
    Session2 = sqlalchemy.orm.sessionmaker()
    Session2.configure(bind=engine)
    session = Session2()
    datas: list[HumidityValue] = session.query(HumidityValue).all()
    csv_out = "TIMESTAMP;HUMIDITY (%);TEMPERATURE (°C)\n"
    for data in datas:
        csv_out += f"{data.datetime.isoformat()};{data.humidity:0.1f};{data.temperature:0.1f}\n"
    return Response(csv_out, 
                    mimetype='text/plain',
                    headers={'Content-disposition': 'attachment; filename=humidity.csv'})


if __name__ == "__main__":
    socketio.run(debug=True, host="0.0.0.0", port=8080)
    # app.run(port=7005)