# -*- coding: utf-8 -*-
"""ULMFiT.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1GkCg0di-a65uoekZbD6xZ6NqXQe7socW

## ULMFiT model for Twitter US Airlines Sentiment
"""

# Import necessary libraries.
import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.preprocessing import LabelEncoder

# We disable warnings & only show errors of TensorFlow.
tf.logging.set_verbosity(tf.logging.ERROR)

"""Now read **Twitter.csv** file as a Pandas dataframe, randomize data & see first 10 records of features, targets from dataframe."""

# Read data in CSV file as a Pandas DataFrame.
twitter_df = pd.read_csv('Tweets.csv', sep=',')

# Now randomize data using permutation to avoid trouble if the data is in some sorted order.
twitter_df = twitter_df.reindex(np.random.permutation(twitter_df.index))

# Take a look at our features (i.e. 'text' & 'airline') & target (i.e. 'airline_sentiment') of dataframe.
twitter_df[['text', 'airline', 'airline_sentiment']].head(10)

"""Here, in feature column '**text**', we have some non-ASCII characters (e.g. emoji) like ™, œ. So we clean-up our text data using following function:"""

def clean_non_ascii(text):
    """
    Function to remove all non-ASCII characters (e.g. emoji) from given text.
    :param text: Text of review from user in data.
    :return: Text string with removed all non-ASCII characters from it.
    """
    return ''.join(i for i in text if ord(i) < 128)

# Let's apply this function to our 'text' feature column in dataframe.
twitter_df['text'] = twitter_df['text'].apply(func=clean_non_ascii)

"""We create four dataframes respectively for: 
**Train features**, **Train targets**, **Test features**, **Test targets**. <br />
That's because to separate training & testing sets.
"""

train_features = pd.DataFrame()
train_targets = pd.DataFrame()
test_features = pd.DataFrame()
test_targets = pd.DataFrame()

# Take first 10000 records for training features & targets respectively.
train_features['text'] = twitter_df['text'].head(n=10000)
train_features['airline'] = twitter_df['airline'].head(n=10000)
train_targets['airline_sentiment'] = twitter_df['airline_sentiment'].head(n=10000)

# Similarly features & targets above 10000 records will be for test.
test_features['text'] = twitter_df['text'].iloc[len(train_features.index):]
test_features['airline'] = twitter_df['airline'].iloc[len(train_features.index):]
test_targets['airline_sentiment'] = twitter_df['airline_sentiment'].iloc[len(train_targets.index):]

"""Now inspect how many **airline** companies & unique classes **airline_sentiment** are present using `describe()` method:"""

print(" {*} Details of 'airline' feature column: \n", twitter_df['airline'].describe(), \
      "\n\n {*} Details of 'airline_sentiment' target column: \n", twitter_df['airline_sentiment'].describe())

"""So here '**`unique`**' section of both results shows the actual unique records in those dataframe columns. It means **6** companies of '**airline**' (feature) & **3** classes of '**airline_sentiment**' (target).

We have '**airline**' (feature) & '**airline_sentiment**' (target) in text form. So let's use ***One-hot encoding*** to convert string format to processable numeric format. <br/> We first convert string to integer and then integer to one-hot encoding.
"""

# First use 'LabelEncoder()' in Scikit-learn to convert from string to integer then use 'to_categorical()' of Keras to get respective one-hot encoding.
# One-hot encoding for training set 'airline' feature:
label_encoder_train_airline = LabelEncoder()
train_airline_feature_int = label_encoder_train_airline.fit_transform(y=train_features['airline'])
train_airline_feature_encoded = tf.keras.utils.to_categorical(y=train_airline_feature_int, 
                                                              num_classes=train_features['airline'].describe()['unique'])

# One-hot encoding for test set 'airline' feature:
label_encoder_test_airline = LabelEncoder()
test_airline_feature_int = label_encoder_test_airline.fit_transform(y=test_features['airline'])
test_airline_feature_encoded = tf.keras.utils.to_categorical(y=test_airline_feature_int, 
                                                             num_classes=test_features['airline'].describe()['unique'])

# Conversion for training targets 'airline_sentiment':
label_encoder_train_targets = LabelEncoder()
train_targets_int = label_encoder_train_targets.fit_transform(y=train_targets['airline_sentiment'])
train_targets_encoded = tf.keras.utils.to_categorical(y=train_targets_int, 
                                                      num_classes=train_targets['airline_sentiment'].describe()['unique'])

# Similarly conversion for test targets 'airline_sentiment':
label_encoder_test_targets = LabelEncoder()
test_targets_int = label_encoder_test_targets.fit_transform(y=test_targets['airline_sentiment'])
test_targets_encoded = tf.keras.utils.to_categorical(y=test_targets_int, 
                                                     num_classes=test_targets['airline_sentiment'].describe()['unique'])

# Let's see how encoding is done.
print(' {*} Oirginal train targets: \n', train_targets['airline_sentiment'].head(5), \
     '\n\n {*} One-hot encoded train targets: \n', [train_targets_encoded[i] for i in range(5)])

"""The feature column '**text**' has textual setences so we use `Tokenizer` that vectorize collection of written text into sequence of integers. That means we use **word embedding**. <br />First we create an object of `Tokenizer` & define a function that fits tokenizer on given text and then return the sequence of integers for that text:"""

# Create Tokenizer object.
tokenizer = tf.keras.preprocessing.text.Tokenizer()

def get_tokenizer_encoding(text=""):
  """
  Function to get sequence of integers for given text.
  :param text: Text of review from user in data.
  :return: Sequence or vector of integers for given text.
  """
  tokenizer.fit_on_texts(texts=text)
  return tokenizer.texts_to_sequences(texts=text)

# Transform and get tokenize encoded text features.
train_text_feature_tokenize_encoded = get_tokenizer_encoding(text=train_features['text'])
test_text_feature_tokenize_encoded = get_tokenizer_encoding(text=test_features['text'])

# Let's check how the sequence is encoded for first sentence in text data.
print(' Original sentence: ', train_features['text'][0], '\n Encoded sequence: ', train_features_tokenize_encoded[0])

"""We have to get maximum sequence length of encoded text between train & test data, to make all sequences of equal length.
<br/>Then use `pad_sequences()` of Keras in order to get every encoded text sequence having the same length. Since we can't use sequences of different lengths for processing.
"""

# Initially get maximum length of encoded text between train & test encoded data.
max_length_text = len(max(train_features_tokenize_encoded, key=len)) \
    if len(max(train_features_tokenize_encoded, key=len)) > len(max(test_features_tokenize_encoded, key=len)) \
    else len(max(test_features_tokenize_encoded, key=len))
print(' Maximum length of encoded text sequence: ', max_length_text)

# Get equal sequence lengths using 'pad_sequences()' for train & test sets.
train_text_feature_padded = tf.keras.preprocessing.sequence.pad_sequences(sequences=train_text_feature_tokenize_encoded,
                                                                          truncating='pre', padding='post',
                                                                          maxlen=max_length_text)

test_text_feature_padded = tf.keras.preprocessing.sequence.pad_sequences(sequences=test_text_feature_tokenize_encoded,
                                                                         truncating='pre', padding='post',
                                                                         maxlen=max_length_text)
print(' {*} Padded sequences with equal shapes ', train_features_padded[0].shape, ' each (training features): \n')
print(train_features_padded)

"""Now we have to get total vocabulary size which is necessary for embedding (first) layer in the analysis model."""

# Get total vocabulary size using 'word_index' property of tokenizer object which is required for embedding layer in our model.
vocabulary_size = len(tokenizer.word_index) + 1  # Adding 1 because of reserved 0 index.
print(' The vocabulary size for our data is: ', vocabulary_size)

"""Next we'll define our model to train & test on data. <br />
Model architecture: <br />
**1. Embedding layer** -> This is the first layer in our model since we have text as word embeddings in feature. So it is important to learn those embeddings. <br />
**2. LSTM** -> Long Short-Term Memory are hidden layers that can maintain their state, which allows to handle sentences where next word depends on previous. Our model's feautre is textual sentences (with word embeddings) so we provided two LSTMs with 100 memory cells each since more memory cells & deeper network may get better results. <br />
**3. Dense** -> Dense is fully connected layer which connects 100 neurons of LSTM in hidden layer to interpret the features extracted from sequence. At the end, another Dense layer with 'softmax' activation is used with 3 neurons to get result among the possible three classes of target (i.e. negative, neutral or positive).
"""

# Define model.
model = tf.keras.models.Sequential()
model.add(tf.keras.layers.Embedding(input_dim=vocabulary_size, input_length=max_length_text,
                                    output_dim=50))
model.add(tf.keras.layers.LSTM(units=100, return_sequences=True))
model.add(tf.keras.layers.LSTM(units=100))
model.add(tf.keras.layers.Dense(units=100, activation='relu'))
model.add(tf.keras.layers.Dense(units=3, activation='softmax'))

print(' {*} Model architecture: \n')
print(model.summary())

# Compile model.
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

print('\n\n Training model... \n')
model.fit(x=[train_text_feature_padded, train_airline_feature_encoded], y=train_targets_encoded,
          batch_size=64, epochs=10, steps_per_epoch=100)
print('\n\n Training finished... \n')

"""After training, we'll evaluate model on test data:"""

# Evaluate model on test data.
loss_acc = model.evaluate(x=[test_text_feature_padded, test_airline_feature_encoded], y=test_targets_encoded, verbose=1)
print(' Test data:= Loss: %0.6f, Accuracy: %0.2f%%' % (loss_acc[0], loss_acc[1] * 100))

"""Our model can correctly classify  more than half of given data (62.65%) on training with just 10000 records. <br />
This can be improved significantly by providing more training data to the model, which will increase its vocabulary size also. Another way may be using set of pre-built embeddings such as **GloVe ("global vectors for word representation")**, which is constructed using the text of Wikipedia. <br />
So here, by creating embeddings on the fly our model performed good on test data with limited set of training.
"""