
import sys
import os
import pickle
import numpy as np

# Mock classes to allow loading
class NetworkSecurityException(Exception): pass

# Add pwd to path
sys.path.append(os.getcwd())

def load_object(file_path):
    try:
        with open(file_path, "rb") as file_obj:
            return pickle.load(file_obj)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return None

try:
    preprocessor = load_object("final_model/preprocessor.pkl")
    if preprocessor:
        print(f"Preprocessor Type: {type(preprocessor)}")
        
        # Check expected features
        n_features = getattr(preprocessor, 'n_features_in_', None)
        print(f"Expected Features: {n_features}")
        
        if n_features:
            # Create dummy numpy array
            dummy_input = np.random.rand(1, n_features)
            print("Attempting transform with Numpy array...")
            try:
                preprocessor.transform(dummy_input)
                print("SUCCESS: Preprocessor accepts Numpy arrays!")
            except Exception as e:
                print(f"FAILURE: Preprocessor transformation failed: {e}")
        else:
             print("Could not determine n_features_in_")

except Exception as e:
    print(f"Error checking preprocessor: {e}")
