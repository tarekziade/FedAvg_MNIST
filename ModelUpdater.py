import os
import onnx
import numpy as np
from onnx import numpy_helper

# Directory setup
HERE = os.path.dirname(__file__)
UPDATED_MODEL_PATH = os.path.join(HERE, "model", "inference.onnx")

class ModelUpdater:
    def __init__(self, updated_model_path, learning_rate=0.01):
        self.updated_model_path = updated_model_path
        self.learning_rate = learning_rate
        self.fc1_weights = []
        self.fc1_bias = []
        self.fc2_weights = []
        self.fc2_bias = []
    
    def update_weights(self, updated_weights):
        """Store the weights from a client for averaging later."""
        fc1_weight_array = np.array(updated_weights[:392000], dtype=np.float32).reshape(500, 784)
        fc1_bias_array = np.array(updated_weights[392000:392500], dtype=np.float32).reshape(500, )
        fc2_weight_array = np.array(updated_weights[392500:397500], dtype=np.float32).reshape(10, 500)
        fc2_bias_array = np.array(updated_weights[397500:], dtype=np.float32).reshape(10, )
        
        self.fc1_weights.append(fc1_weight_array)
        self.fc1_bias.append(fc1_bias_array)
        self.fc2_weights.append(fc2_weight_array)
        self.fc2_bias.append(fc2_bias_array)
        
        print(f"Received data from {len(self.fc1_weights)} clients out of 50 clients")

    def average_parameters(self, parameters_list):
        """Average the parameters collected from all clients."""
        if len(parameters_list) == 0:
            return None
        
        return np.mean(parameters_list, axis=0).astype(np.float32)

    def copy_to_model(self, model, name, params):
        """Copy the averaged parameters to the ONNX model."""
        print(f"Updating parameters of {name}")
        for initializer in model.graph.initializer:
            if initializer.name == name:
                new_weights_tensor = numpy_helper.from_array(params, name=initializer.name)
                initializer.CopyFrom(new_weights_tensor)

    def update_model(self):
        """Update the ONNX model with the averaged parameters."""
        if not self.fc1_weights:
            print("No user data to process")
            return {"message": "No user data to process"}
        
        print("Loading the model")
        model = onnx.load(self.updated_model_path)
        
        # Average the parameters
        print("Start averaging the parameters")
        fc1_weight_avg = self.average_parameters(self.fc1_weights)
        fc1_bias_avg = self.average_parameters(self.fc1_bias)
        fc2_weight_avg = self.average_parameters(self.fc2_weights)
        fc2_bias_avg = self.average_parameters(self.fc2_bias)
        
        # Update the model with the averaged parameters
        print("Start updating the model parameters")
        self.copy_to_model(model, "fc1.weight", fc1_weight_avg)
        self.copy_to_model(model, "fc1.bias", fc1_bias_avg)
        self.copy_to_model(model, "fc2.weight", fc2_weight_avg)
        self.copy_to_model(model, "fc2.bias", fc2_bias_avg)
        
        print("Saving the model")
        onnx.save_model(model, self.updated_model_path)
        print("Model saved successfully.")
        print("Emptying the weights")
        self.reset()
        return {"message": "Model updated with averaged parameters"}

    def reset(self):
        """Clear all accumulated weights and biases."""
        self.fc1_weights = []
        self.fc1_bias = []
        self.fc2_weights = []
        self.fc2_bias = []
        print("Reset all weight and bias lists.")
        
# Example usage
if __name__ == "__main__":
    updater = ModelUpdater(updated_model_path=UPDATED_MODEL_PATH)
    # Example: Pass the weights collected from clients to `update_weights` method
    # updated_weights = ... (collected from clients)
    # updater.update_weights(updated_weights)
    updater.update_model()
