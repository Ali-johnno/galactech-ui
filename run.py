#! /usr/bin/env python
from pyexpat import model
from app import app
from dataprocess import AudioPreProc, DataGenerator
from rnnt import RNNT3

#
import matplotlib.pyplot as mpl 
import numpy as np
import librosa as lb
import librosa.display
import random
import tensorflow as tf
from tensorflow import keras
from keras import callbacks

def single_file_preprocessing(sample_data):
  (aud,sr) = AudioPreProc.open(sample_data)   
  tot = AudioPreProc.rechannel((aud,sr), 1)
  tot=AudioPreProc.pad_trunc(tot,12000)            
  mfcc,hop=AudioPreProc.get_mfccs(tot)
  
  f0=AudioPreProc.get_fundamental_freq(tot,hop)
  f0=f0.reshape((1,f0.shape[0]))
  energy=AudioPreProc.get_energy(tot,hop)
  fin=np.concatenate([mfcc,f0,energy])
  return fin


if __name__ == "__main__":

    print("* Loading Keras model and Flask starting server..."
           "please wait until server has fully started")

    sample_data='supplement/LJ01-516.wav'
    ## Variables:
    num_hidden_encoder=512 
    num_hidden_joiner=64  
    num_hidden_predictor=64 
    input_dim=1024 
    num_predictions=2  
    encoder_input_shape=(15,1198) 
    predictor_input_shape=(1,2)
    joiner_input_shape=(160,) 
    batch_size=1
    num_encoder_dense=128
    num_predictor_dense=32
    label=1

    build_data_gen=DataGenerator(np.array([sample_data]),np.array([label]),to_fit=True,batch_size=1, dim=encoder_input_shape)
    

    ## compiling and fitting rnnt
    #RNNT=RNNT3(num_hidden_encoder, num_hidden_predictor, num_hidden_joiner, num_predictions, joiner_input_shape,predictor_input_shape,encoder_input_shape,num_encoder_dense,num_predictor_dense)
    opt = keras.optimizers.Adam(learning_rate=0.001)
    app.config['RNNT'].compile(optimizer=opt, loss='sparse_categorical_crossentropy', metrics=['accuracy'])
    app.config['RNNT'].fit(build_data_gen,epochs=1,verbose=2)

    #load weights from checkpoint file
    app.config['RNNT'].load_weights('supplement/cp_teststep_with64_predictor-epoch0001_acc0.562.ckpt')
    print("RNNT model successfully loaded!! <! !>")
    app.run(debug=True, host="0.0.0.0", port=8080)
