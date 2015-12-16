"""
colorful
Learned color labeling.
Drew Troxell
"""

import atexit
import json

import numpy as np
from peewee import SqliteDatabase, Model, IntegerField, TextField
import serial
from sklearn.neighbors import KNeighborsClassifier

db = SqliteDatabase('colorful.db') # The one true global.
ser = serial.Serial('COM3', 115200, timeout=10) # The other true global.

class BaseModel(Model):
    """ Based Model """
    class Meta:
        database = db

class Sample(BaseModel):
    """ Represents a sample with a label """
    red = IntegerField()
    green = IntegerField()
    blue = IntegerField()
    label = TextField(null=True)

class PredictionProbabilityError(Exception):
    """ Raised when a label is required. """
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class Learn():
    """ Wrappers for fitting and predicting """
    n = 3
    knn = KNeighborsClassifier(n_neighbors=n)
    
    def train(sample, label):
        sample.label = label
        sample.save()
    
    def classify(sample):
        samples = Sample.select()
        X = np.array([[x.red, x.green, x.blue] for x in samples if x.label != None])
        y = np.array([x.label for x in samples if x.label != None])
        if len(y) < Learn.n or len(X) < Learn.n:
            raise PredictionProbabilityError(0)
        Learn.knn.fit(X, y)
        prob = Learn.knn.predict_proba([[sample.red, sample.green, sample.blue]])[0][0]
        return Learn.knn.predict([[sample.red, sample.green, sample.blue]])

def connect():
    """ Identify the serial port and handshake """
    ser.write("connect colorful".encode())
    response = ser.readline().decode()
    data = json.loads(response)
    print("Connected! Device Information:" + response)
    
def capture():
    """ Trigger a reading, store it in the database """
    while input("Capture color? (y): ") != 'y':
        _ = 0
    ser.write("run colorful".encode())
    data = json.loads(ser.readline().decode())
    print("Received from sensor: " + str(data))
    r = data["red"]
    g = data["green"]
    b = data["blue"]
    return Sample.create(red=r, green=g, blue=b)

def main():
    """ Main Loop """
    db.connect()
    db.create_tables([Sample], True)
    
    connect()
    while True:
        sample = capture()
        try:
            label = Learn.classify(sample)
            print(label[0])
            resp = input("Is this correct? (y/n): ").lower()
            if resp == "y":
                Learn.train(sample, label[0])
            else:
                label = input("Give this sample a label: ").lower()
                Learn.train(sample, label)
        except PredictionProbabilityError as e:
            label = input("Not enough training data. Enter a label for this sample: ").lower()
            Learn.train(sample, label)
        db.commit()

@atexit.register
def goodbye():
    ser.write("close colorful".encode())
    print("Exiting Colorful...")

if __name__ == "__main__":
    main()