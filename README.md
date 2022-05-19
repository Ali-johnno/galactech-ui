# GALACTECH ACCENT IDENTIFICATION SYSTEM
The Galactech Identification System is a revolutionary system that makes use of a Recurrent Neural Network Transducer
which uses the feature modeling beforehand concept to give you an pproximation of the accent that
is in the audio input. It uses a trained neural network model that will take your audio as well as 
run it through its model that extracts mel-frequency cepstral coefficient, fundamental frequencies and energy
to gives you the predicted accent that it has identified. Our system however has an accuracy of 56.25% and 
identifies each accent as Trinidadian.

# TEAM MEMBERS

* Kalia-Lee Rodney
* Alexandria Burnett
* Aaliyah Johnston
* Jamar Lee

### HOW TO RUN
Mac OS
```bash
$ python3 -m venv venv (or with you have multiple versions of windows)
$ source venv/bin/activate
$ pip install -r requirements.txt 
$ python3 run.py
```

### HOW TO RUN
Windows or Linux
```bash
$ python -m venv venv 
$ .\venv\Scripts\activate
$ pip install -r requirements.txt 
$ python run.py
```