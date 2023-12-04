from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from io import StringIO
import csv

app = Flask(__name__)

# Replace the following with your MySQL database URI
app.config[
    "SQLALCHEMY_DATABASE_URI"
] = "mysql+pymysql://mohamad:%23%40%2176Mohamad612@127.0.0.1/FYP"

db = SQLAlchemy(app)


class Data(db.Model):
    __tablename__ = "data"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    text = db.Column(db.Text)
    entities = db.Column(db.Text)


@app.route("/get_data", methods=["GET"])
def get_data():
    try:
        # Fetch data from the 'data' table
        data = Data.query.all()

        # Convert the data into the desired format and quote the item
        result = []
        for row in data:
            item = {"data": "('" + row.text + "',{'entities': [" + row.entities + "]})"}
            result.append(item)

        # Save entities to a CSV file
        csv_data = StringIO()
        fieldnames = ["data"]
        csv_writer = csv.DictWriter(csv_data, fieldnames=fieldnames)
        csv_writer.writeheader()
        csv_writer.writerows(result)

        # Save the CSV data to a file
        with open("entities_data.csv", "w", newline="") as file:
            file.write(csv_data.getvalue())

        return jsonify(result)

    except Exception as e:
        return f"Error: {e}"


if __name__ == "__main__":
    app.run(port=5001, debug=True)
