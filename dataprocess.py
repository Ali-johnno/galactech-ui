import matplotlib.pyplot as mpl 
import numpy as np

import librosa as lb
import librosa.display

import random
from tensorflow.keras.utils import Sequence
from scipy import signal



class AudioPreProc:
  def open(file):
    arr, sr = lb.load(file,mono=True,sr=44100) # sampling at 4410Khz instead of standard at 22khz
    return (arr, sr) #returns a numpy array and the sample rate

  @staticmethod
  def rechannel(aud, new_channel=1):
    sig, sr = aud
    #if (sig.shape[0] == new_channel):
    if(len(sig.shape)==new_channel): #changing as libroase says (n,) is mono bu (2,n) is stereo
      return aud
    else:
      # Convert from mono to stereo by duplicating the first channel
      resig=np.array([sig,sig])
    return (resig, sr)

  @staticmethod
  def remove_silence(aud):
    sig,sr=aud
    print("Reg audio ",sig)
    clips = lb.effects.split(sig, top_db=10)
    wav_data = []
    for c in clips:
        data = sig[c[0]:c[1]]
        wav_data.append(data)
    print("Silenced audio ",wav_data)
    return (wav_data, sr)

  @staticmethod
  def pad_trunc(aud,max_ms):
    sig,sr = aud
    sig_len=round(lb.get_duration(sig,sr=sr)*1000)
    max_len = sr//1000 * max_ms
    #print(max_len)

    if (sig_len > max_len):
      # Truncate the signal to the given length
      resig = sig[:,:max_len]
      #print("SIG",sig)
    elif (sig_len < max_len):
      resig=lb.util.fix_length(sig, size=max_len)
    return (resig,sr)

  @staticmethod
  def remove_background(aud):
    sig,sr=aud
    b,a = signal.butter(10, 2000/(sr/2), btype='highpass')
    sig = signal.lfilter(b,a,sig)
    return (sig,sr)

  def get_fundamental_freq(aud,hop):
    sig,sr=aud
    f0 = lb.yin(sig, sr = sr, fmin = lb.note_to_hz('C2'), fmax= lb.note_to_hz('C7'),hop_length=hop)
    norm_f0=np.linalg.norm(f0)
    f0=f0/norm_f0
    return f0

  def get_energy(aud,hop):
    sig,sr=aud
    energy=lb.feature.rms(sig, hop_length=hop, center=True)
    return energy

  def get_mfccs(sig,num_mfccs=13,window_length=0.02):
    aud,sr=sig
    n_fft = int(sr * window_length)   # window length: 0.02 s
    #print(n_fft,n_fft//2)
    hop_length = n_fft // 2  
    mfccs = lb.feature.mfcc(aud, sr=sr, n_mfcc=num_mfccs, hop_length=hop_length, n_fft=n_fft)
    norm_mfcc=np.linalg.norm(mfccs)
    mfccs=mfccs/norm_mfcc
    return mfccs,hop_length

  def get_formant_freq(sig):
    aud,sr=sig
    A = librosa.core.lpc(aud,4)
    rts = np.roots(A)
    rts = rts[np.imag(rts) >= 0]
    angz = np.arctan2(np.imag(rts), np.real(rts))
    frqs = angz * sr / (2 *  np.pi)
    frqs.sort()
    norm_formant=np.linalg.norm(frqs)
    fin=frqs/norm_formant
    makeup=(1198//len(fin))+1
    fin=np.tile(fin,makeup)
    return fin[:1198]


class DataGenerator(Sequence):
    """Generates data for Keras
    Sequence based data generator. Suitable for building data generator for training and prediction.
    """
    def __init__(self, filenames, audlabels, 
                 to_fit=True, batch_size=1, dim=(15,1198),
                 n_channels=1, n_classes=2, shuffle=True):
        """Initialization
        :param filenames: list of audio file names
        :param audlabels: respective accent_id labels for filenames
        :param audio_path: path to audio locations
        :param to_fit: True to return X and y, False to return X only
        :param batch_size: batch size at each iteration
        :param dim: tuple indicating audio dimension
        :param n_channels: number of audio channels
        :param n_classes: number of output masks
        :param shuffle: True to shuffle label indexes after every epoch
        """
        self.audlabels = audlabels
        self.filenames = filenames
        self.to_fit = to_fit
        self.batch_size = batch_size
        self.dim = dim
        self.n_channels = n_channels
        self.n_classes = n_classes
        self.shuffle = shuffle
        self.on_epoch_end()
        self.target_dim=(1,n_classes)
        self.duration = 12000 #length in milliseconds   #rn at 10 seconds
    def __len__(self):
        """Denotes the number of batches per epoch
        :return: number of batches per epoch
        """
        return int(np.floor(len(self.filenames) / self.batch_size))

    def __getitem__(self, index):
        """Generate one batch of data
        :param index: index of the batch
        :return: X and y when fitting. X only when predicting
        """
        # Generate indexes of the batch
        indexes = self.indexes[index * self.batch_size:(index + 1) * self.batch_size]

        # Find list of IDs
        list_IDs_temp = [self.filenames[k] for k in indexes]

        # Generate data
        X,y,target= self._generate_data(list_IDs_temp)

        if self.to_fit:
            return [X, target],y
        else:
            return X

    def on_epoch_end(self):
        """Updates indexes after each epoch
        """
        self.indexes = np.arange(len(self.filenames))
        if self.shuffle == True:
            np.random.shuffle(self.indexes)

    def _generate_data(self, list_IDs_temp):
        # Initialization       
        X = np.empty((self.batch_size, *self.dim),dtype=float)
        y = np.empty((self.batch_size), dtype=float)
        target=np.empty((self.batch_size, *self.target_dim),dtype=float)
        # Generate data
        for i, ID in enumerate(list_IDs_temp):
            # Store sample
            (aud,sr) = AudioPreProc.open(ID)   
            tot=AudioPreProc.remove_background((aud,sr))
            tot=AudioPreProc.pad_trunc(tot,12000)
            
            mfcc,hop=AudioPreProc.get_mfccs(tot)
    
            f0=AudioPreProc.get_fundamental_freq(tot,hop)
            f0=f0.reshape((1,f0.shape[0]))
            #print('FF',f0.shape)
            energy=AudioPreProc.get_energy(tot,hop)
            #print('energy',energy.shape)

            fin=np.concatenate([mfcc,f0,energy])
            X[i,]=fin
            y[i] = self.audlabels[i]  
           
            target[i,]=np.array([np.random.uniform(low=0.1,high=0.5) if self.audlabels[i]!=x else np.random.uniform(low=0.5,high=0.1) for x in range(self.n_classes)]).reshape((1,self.n_classes))
        return X,y,target
