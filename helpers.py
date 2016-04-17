from __future__ import print_function

import numpy as np
import math
import matplotlib.pyplot as plt
import pandas as pd


def make_training_vectors(text_train, unroll=20, step=3):
    sentences = []
    next_chars = []
    n_train = len(text_train)
    chars = set(text_train)
    char_indices = dict((c, i) for i, c in enumerate(chars))
    indices_char = dict((i, c) for i, c in enumerate(chars))
    for i in range(0, n_train - unroll, step):
        sentences.append(text_train[i: i + unroll])
        next_chars.append(text_train[i + unroll])
    X = np.zeros((len(sentences), unroll, len(chars)), dtype=np.bool)
    y = np.zeros((len(sentences), len(chars)), dtype=np.bool)
    for i, sentence in enumerate(sentences):
        for t, char in enumerate(sentence):
            X[i, t, char_indices[char]] = 1
        y[i, char_indices[next_chars[i]]] = 1
    return [X,y]


def entropy(pred):
    return sum([- p * math.log(p) for p in pred])

def sample(a, temperature=1.0):
    # samples an index from a probability array;
    # higher temperature raises the entropy and vice versa
    a = np.log(a) / temperature
    a = np.exp(a) / np.sum(np.exp(a))
    return np.argmax(np.random.multinomial(1, a, 1))


def df_from_sequence(sequence, chars, model, unroll):
	results = []
	length = len(sequence) - unroll
	window = sequence[:unroll]
	char_indices = dict((c, i) for i, c in enumerate(chars))
	indices_char = dict((i, c) for i, c in enumerate(chars))
    
	for i in range(length):

		# predict from model:
		x = np.zeros((1, unroll, len(chars)))
		for t, char in enumerate(window):
			x[0, t, char_indices[char]] = 1.
		preds = model.predict(x, verbose=0)[0]

		# find current, next and predicted characters; and advance window:
		this_char = window[unroll-1]
		next_char = sequence[unroll + i]
		predicted = np.argmax(preds)
		window = list(window[1:]) + list(next_char)

		# record results:
		results.append((this_char,
                        next_char,
                        preds[char_indices[next_char]],
                        indices_char[predicted],
                        preds[predicted],
                        entropy(preds)
                        ))

	# make into data frame:
	df = pd.DataFrame(results)
	df.columns = ["current","next","next_prob","pred","pred_prob","entropy"]
	return df


def model_view(df, chars, dotsize=0.1):
    print("Nr data points:", df.shape[0])
    print("Correct prediction:", sum(df.next==df.pred)/float(df.shape[0]))
    plt.figure(figsize=(20,20))
    ax1 = plt.subplot2grid((5,5), (0, 0), colspan=2)
    ax2 = plt.subplot2grid((5,5), (0, 2), colspan=2)
    ax3 = plt.subplot2grid((5,5), (1, 0), rowspan=2, colspan=2, sharex=ax1)
    ax4 = plt.subplot2grid((5,5), (1, 2), rowspan=2, colspan=2, sharex=ax2, sharey=ax3)
    ax5 = plt.subplot2grid((5,5), (1, 4), rowspan=2, sharey=ax3)
    ax1.hist(df['pred_prob'], color='lightgrey', bins=20)
    ax1.set_title("Prediction (max) probabilities")
    ax2.hist(df['entropy'], color='lightgrey', bins=20)
    ax2.set_title("Prediction entropies")
    ax3.scatter(df['pred_prob'], df['next_prob'], s=dotsize)
    ax3.set_title("Probability of actual against max probability")
    # some embellishments for the 4th plot:
    N = len(chars)
    y = np.arange(0.01,0.99,0.01)
    x = [-p*math.log(p)-(1-p)*math.log(1-p) for p in y]
    z = [-p*math.log(p)-(N-1)*(1-p)/(N-1)*math.log((1-p)/(N-1)) for p in y]
    ax4.scatter(df['entropy'], df['next_prob'], s=0.1)
    ax4.plot(x,y, c='green')
    ax4.plot(z,y, c='red')
    ax4.scatter(df['entropy'], df['next_prob'], s=dotsize)
    ax4.set_title("Probability of actual against entropy")
    ax5.hist(df['next_prob'], color='lightgrey', bins=20, orientation='horizontal')
    ax5.set_title("Probability of actual")
    plt.show()

