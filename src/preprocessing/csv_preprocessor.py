import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

def load_and_preprocess(csv_path, test_size=0.2, normalize=True, random_state=42):
    """
    Loads alerts from CSV, splits into train/test and optionally normalizes numeric columns.
    
    Args:
        csv_path (str): Path to CSV file.
        test_size (float): Fraction of data to reserve for testing.
        normalize (bool): Whether to normalize numeric features.
        random_state (int): Random seed.
        
    Returns:
        X_train, X_test, y_train, y_test
    """
    df = pd.read_csv(csv_path)

    # Example: create a binary target based on severity
    df['target'] = (df['severity'] == 'critical').astype(int)

    # Drop unnecessary columns
    X = df.drop(columns=['severity', 'target', 'description', 'summary', 'startsAt', 'endsAt'])
    y = df['target']

    # One-hot encode categorical variables
    X = pd.get_dummies(X, columns=['job', 'instance', 'status'])


    # Split into train and test sets
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )

    if normalize:
        scaler = StandardScaler()
        X_train = scaler.fit_transform(X_train)
        X_test = scaler.transform(X_test)

    return X_train, X_test, y_train, y_test
