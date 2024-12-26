from src.api.rpc_client import *
import requests

if __name__ == "__main__":
    # Initialize DatasetManager
    dataset_manager = DatasetManager('../../components/prompt_engineering_dataset.csv')

    if dataset_manager.df is None:
        print("Error: Dataset is not available. Exiting.")
        exit(1)

    # Iterate through the dataset's 'Prompt' column
    for m in dataset_manager.df['Prompt']:
        print(f"Sending prompt: {m}")
        try:
            headers = {
                'Content-Type': 'application/json',
            }

            data = {
                'm': f'{m}',
            }

            requests.post('http://0.0.0.0:8000/prompt', json=data, headers=headers)
        except Exception as e:
            print(f"Error: An unexpected error occurred for prompt '{m}': {e}")
