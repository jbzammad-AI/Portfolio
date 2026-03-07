import pandas as pd
import os

def save_csv_individual(data_list, original_filename, output_folder="data/processed"):
    """
    Save each invoice's data into a separate CSV named after the uploaded file.
    """
    # Ensure folder exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Clean filename (replace spaces with underscores)
    base_name = os.path.splitext(os.path.basename(original_filename))[0]
    output_path = os.path.join(output_folder, f"{base_name}.csv")

    # Save CSV
    df = pd.DataFrame(data_list)
    df.to_csv(output_path, index=False)

    return output_path  # return path for Streamlit download
