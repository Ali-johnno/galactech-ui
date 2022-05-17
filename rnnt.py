import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
#import torch
from keras.models import Sequential
from keras.layers import LSTM
from keras.layers import Dense
from keras.layers import Embedding
from keras.layers import InputLayer
from keras.utils.np_utils import to_categorical

class Encoder(keras.layers.Layer):
  def __init__(self,num_hidden_encoder,encoder_input_shape,num_encoder_dense):
    super(Encoder,self).__init__()
    self.num_hidden_e=num_hidden_encoder
    self.input_shape_e=encoder_input_shape
    self.num_enc_dense=num_encoder_dense
    self.e_input=InputLayer(input_shape=self.input_shape_e,name="encoder_input",dtype=tf.float64)
    self.e_masking=layers.Masking(mask_value=0.0,input_shape=self.input_shape_e)
    self.l1= LSTM(self.num_hidden_e,return_sequences=True,dropout=0.1,name="e_lstm1")
    self.l2= LSTM(self.num_hidden_e,return_sequences=True,dropout=0.1,name="e_lstm2")
    #self.l3= LSTM(self.num_hidden_e,return_sequences=True,dropout=0.1,name="e_lstm3")
    self.l4= LSTM(self.num_hidden_e,return_sequences=True,dropout=0.1,name="e_lstm4")
    self.e_dense=Dense(self.num_enc_dense) 
   

  def call(self, input, is_sequence=False):
    i= self.e_input(input)
    mask_out=self.e_masking(i)
    output=self.l1(mask_out)
    output=self.l2(output)
    #output=self.l3(output)
    output=self.l4(output)
    fin=self.e_dense(output)
    if is_sequence:
      return fin
    else:
      return fin[:,-1]

    
  def initialize_states(self, batch_size=32):    
    return (tf.zeros([batch_size, self.num_hidden_e],tf.float32),
                tf.zeros([batch_size, self.num_hidden_e], tf.float32))
    
  def get_config(self):
    config = super(Encoder, self).get_config()
    #config={}
    config.update({"num_hidden_encoder": self.num_hidden_e})
    config.update({"encoder_input_shape": self.input_shape_e})
    return config

class Single_Step_Predictor(keras.layers.Layer):

  def __init__(self, num_hidden_predictor,predictor_input_shape,num_predictor_dense):
    super(Single_Step_Predictor,self).__init__()
    self.num_hidden_p=num_hidden_predictor
    self.num_pred_dense=num_predictor_dense
    self.input_shape_p=predictor_input_shape
    self.p_input=InputLayer(input_shape=self.input_shape_p,name="input_predictor")
    self.pl1= LSTM(self.num_hidden_p,return_state=True,dropout=0.1,name="p_lstm")
    #self.pl2= LSTM(self.num_hidden_p,return_state=True, dropout=0.2)
    self.p_dense=Dense(self.num_pred_dense)

  def call(self, input, state_h,state_c):
    i=self.p_input(input)
    output,hidd_state, cell_state=self.pl1(i,initial_state=[state_h,state_c])
    fin=self.p_dense(output)

    return fin, hidd_state, cell_state

  def initialize_states(self, batch_size=4):    
    return (tf.zeros([batch_size, self.num_hidden_p],tf.float32),
                tf.zeros([batch_size, self.num_hidden_p],tf.float32))
  
  def get_config(self):
    config = super(Single_Step_Predictor, self).get_config()
    #config={}
    config.update({"num_hidden_predictor": self.num_hidden_p})
    config.update({"predictor_input_shape": self.input_shape_p})
    return config

class Joiner(keras.layers.Layer):
  def __init__(self, num_hidden_joiner, joiner_input_shape, num_predictions):
    super(Joiner,self).__init__()
    self.num_hidden_j=num_hidden_joiner
    self.input_shape_j=joiner_input_shape
    self.num_predictions=num_predictions
    self.j_input=InputLayer(input_shape=self.input_shape_j,name="joiner_input")
    self.d1= Dense(self.num_hidden_j,activation=None,name="joiner_dense",input_shape=self.input_shape_j)
    self.d2=Dense(self.num_predictions,activation='softmax')
    
  
  def call(self, input):
    i=self.j_input(input)
    intermediate=self.d1(i)
    fin= self.d2(intermediate)

    return fin

  def get_config(self):

    config = super(Joiner, self).get_config()
    config.update({"num_hidden_joiner": self.num_hidden_j})
    config.update({"joiner_input_shape": self.input_shape_j})
    config.update({"num_predictions":self.num_predictions})
    return config

class RNNT3(keras.Model):
  def __init__(self, num_hidden_encoder, num_hidden_predictor, num_hidden_joiner, num_predictions, joiner_input_shape,predictor_input_shape,encoder_input_shape,num_encoder_dense,num_predictor_dense):
    super(RNNT3,self).__init__()
    self.num_hidden_encoder=num_hidden_encoder
    self.num_hidden_predictor=num_hidden_predictor
    self.num_hidden_joiner=num_hidden_joiner
    self.num_predictions=num_predictions
    self.num_enc_dense=num_encoder_dense
    self.num_pred_dense=num_predictor_dense
    self.joiner_input_shape=joiner_input_shape
    self.predictor_input_shape=predictor_input_shape
    self.encoder_input_shape=encoder_input_shape
    self.encoder=Encoder(self.num_hidden_encoder,self.encoder_input_shape,num_encoder_dense)
    self.predictor=Single_Step_Predictor(self.num_hidden_predictor,self.predictor_input_shape,num_predictor_dense)
    self.joiner=Joiner(self.num_hidden_joiner, self.joiner_input_shape, self.num_predictions)

  def call(self, inputs):
    pred_init=self.predictor.initialize_states(1)
    hid,cell=pred_init[0],pred_init[1]
    encoder_out=self.encoder(inputs[0],is_sequence=False) 
    pred_out,hid,cell=self.predictor(inputs[1],hid,cell)  ## only expecting 1 value from y but we need two
    joiner_input=tf.concat([encoder_out,pred_out],axis=1)
    fin=self.joiner(joiner_input)
    return fin

 
  def one_step_decode(self,encoder_out,timestep):
    """
    Decoding for every element we get in the 
    """
    prev_predict=[]
    pred_init=self.predictor.initialize_states(1)
    state_h=pred_init[0]
    state_c=pred_init[1]
    pred_out=np.array([[0.5,0.5]]).reshape(self.predictor_input_shape)
    for step in range(self.encoder_input_shape[0]):
        pred_out, state_h, state_c = self.predictor(tf.reshape(pred_out,[1,1,2]), state_h,state_c,training=False)
        joiner_input=tf.concat([tf.reshape(encoder_out[step],[1,self.num_enc_dense]),pred_out],axis=1) ##change to num_hidden_encoder
        pred_out=self.joiner(joiner_input,training=False)
        prev_predict=pred_out
    return tf.convert_to_tensor(prev_predict)

  @tf.function
  def make_prediction(self,input,batch_size):
    prev_predict=tf.TensorArray(tf.float32,size=batch_size)
    np_output=tf.TensorArray(tf.int64, size=batch_size)

    argmax_outputs=tf.TensorArray(tf.float32, size=batch_size)

    encoder_outputs= self.encoder(input, is_sequence=True,training=False)

    ins=tf.convert_to_tensor(encoder_outputs)

    timesteps = ins.shape[1]
    pred_init=self.predictor.initialize_states(batch_size)
    state_h=pred_init[0]
    state_c=pred_init[1]
    pred_out=tf.reshape([0.5 for i in range(batch_size*self.num_predictions)],[batch_size,1,num_predictions])
    for step in range(self.encoder_input_shape[0]):
      pred_out, state_h, state_c = self.predictor(tf.reshape(pred_out,[batch_size,1,2]), state_h,state_c,training=False)
      joiner_input=tf.concat([tf.reshape(ins[:,step],[batch_size,self.num_enc_dense]),pred_out],axis=1) ##change to num_hidden_encoder
      pred_out=self.joiner(joiner_input,training=False)
      prev_predict=pred_out

    np_output=tf.math.argmax(prev_predict)
    argmax_output=prev_predict

    return np_output, argmax_output

  def predict_val(self,input,batch_size):
    np_output=[]
    argmax_outputs=[]
    encoder_outputs= self.encoder(input, is_sequence=True,training=False)
    ins=tf.convert_to_tensor(encoder_outputs)
    timesteps = ins.shape[1]
    print(ins.shape)
    for i in range(batch_size): # for every input in the batch
        decoded_seq = self.one_step_decode(ins[i], timesteps)
        np_output.append(np.argmax(decoded_seq))    
        argmax_outputs.append(decoded_seq)
    return np_output,argmax_outputs

  @tf.function
  def test_step(self, data):
    # Unpack the data
    X, y = data
    # Compute predictions
    y_pred_not_np, raw = self.make_prediction(X[0],1)
    raw=tf.reshape(raw,[1,2])
    # Updates the metrics tracking the loss
    self.compiled_loss(tf.convert_to_tensor(y),tf.convert_to_tensor(raw) ,regularization_losses=self.losses)
    # Update the metrics.
    self.compiled_metrics.update_state(tf.convert_to_tensor(y),tf.convert_to_tensor(raw))
    # Return a dict mapping metric names to current value.
    # Note that it will include the loss (tracked in self.metrics).
    return {m.name: m.result() for m in self.metrics}


