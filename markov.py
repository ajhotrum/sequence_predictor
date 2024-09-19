from collections import defaultdict
from sklearn.model_selection import train_test_split
import pandas as pd

df = pd.read_csv('atom_connections.csv')

# Step 1: Split data into training and test sets
train_data, test_data = train_test_split(df, test_size=0.2, random_state=42)

# Step 2: Train the Markov Chain model on the training set
# Rebuild transitions using only training data
transitions_train = defaultdict(lambda: defaultdict(int))

for _, row in train_data.iterrows():
    source = row['Source Atom']
    target = row['Target Atom']
    transitions_train[source][target] += 1

# Convert the counts into probabilities
transition_probabilities_train = {}
for source, targets in transitions_train.items():
    total = sum(targets.values())
    transition_probabilities_train[source] = {target: count / total for target, count in targets.items()}

# Predict function (same as before)
def predict_next(current_word):
    if current_word not in transition_probabilities_train:
        return None  # No next word predicted
    next_word = max(transition_probabilities_train[current_word], key=transition_probabilities_train[current_word].get)
    return next_word

# Step 3: Evaluate the accuracy on the test set
correct_predictions = 0
total_predictions = 0

for _, row in test_data.iterrows():
    source = row['Source Atom']
    actual_next = row['Target Atom']
    predicted_next = predict_next(source)
    
    if predicted_next == actual_next:
        correct_predictions += 1
    total_predictions += 1

# Step 4: Calculate accuracy
accuracy = correct_predictions / total_predictions
print(f"Accuracy: {accuracy:.2%}")
