import pandas as pd
from collections import defaultdict, Counter
import random
from sklearn.model_selection import train_test_split

# Create second-order Markov chain
def create_second_order_markov_chain(data):
    markov_chain = defaultdict(Counter)
    for i in range(len(data) - 2):
        current_state = (data[i], data[i + 1])
        next_state = data[i + 2]
        markov_chain[current_state][next_state] += 1
    return markov_chain

# Predict the next word based on the last two words
def predict_next_word(markov_chain, current_state):
    next_word_probs = markov_chain.get(current_state, None)
    if not next_word_probs:
        return None
    return max(next_word_probs, key=next_word_probs.get)  # Most probable next word

# Evaluate the model's performance
def evaluate_model(markov_chain, test_data):
    correct_predictions = 0
    total_predictions = 0

    for i in range(len(test_data) - 2):
        current_state = (test_data[i], test_data[i + 1])
        actual_next_word = test_data[i + 2]
        predicted_next_word = predict_next_word(markov_chain, current_state)

        if predicted_next_word == actual_next_word:
            correct_predictions += 1
        total_predictions += 1

    # Calculate accuracy
    accuracy = correct_predictions / total_predictions if total_predictions > 0 else 0
    return accuracy

# Sample CSV data
df = pd.read_csv('atom_connections.csv')

# Extract the sequence of "Source Atom" and "Target Atom"
sequence_data = df['Source Atom'].tolist() + df['Target Atom'].tolist()

# Split the data into training and testing sets
train_data, test_data = train_test_split(sequence_data, test_size=0.2, random_state=42)

# Create the second-order Markov chain using the training data
markov_chain = create_second_order_markov_chain(train_data)

# Evaluate the model on the test data
accuracy = evaluate_model(markov_chain, test_data)

# Output the accuracy
print(f"Model Accuracy: {accuracy * 100:.2f}%")
