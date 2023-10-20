import os
import csv
import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LinearRegression
from scipy.signal import find_peaks

class RotatingDiskElectrodeAnalyzer:
    def __init__(self, folder_path):
        self.folder_path = folder_path
        self.file_paths = self._get_file_paths()
        self.data = []

    def _get_file_paths(self):
        file_paths = []
        for root, dirs, files in os.walk(self.folder_path):
            for file in files:
                if file.endswith(".csv"):
                    file_paths.append(os.path.join(root, file))
        return file_paths

    def analyze_files(self):
        for file_path in self.file_paths:
            self.analyze_file(file_path)



    def calculate_baseline_slope(self, baseline_data):
        time_column = "Corrected time (s)"
        current_column = "WE(1).Current (A)"

        baseline_time = np.array([float(row[time_column]) for row in baseline_data]).reshape(-1, 1)
        baseline_current = np.array([float(row[current_column]) for row in baseline_data])

        # Perform linear regression
        regression_model = LinearRegression()
        regression_model.fit(baseline_time, baseline_current)

        # Return the slope (baseline correction factor)
        return regression_model.coef_[0]

    def correct_current(self, time_data, raw_current_data, slope):
        corrected_current_data = [raw_current - (time * slope) for time, raw_current in
                                  zip(time_data, raw_current_data)]
        return corrected_current_data

    def find_plateaus(self, corrected_current_data):
        corrected_current_array = np.array(corrected_current_data)
        plateau_indices, _ = find_peaks(-corrected_current_array, distance=10)

        return plateau_indices

    def perform_standard_curve_regression(self, concentrations, plateau_indices):
        concentration_array = np.array(concentrations).reshape(-1, 1)
        plateau_data = [self.data[idx]["corrected_current"][plateau_indices[idx]] for idx in range(len(self.data))]
        plateau_data_array = np.array(plateau_data)

        regression_model = LinearRegression()
        regression_model.fit(concentration_array, plateau_data_array)

        slope = regression_model.coef_[0]
        intercept = regression_model.intercept_
        return slope, intercept

    def analyze_file(self, file_path):
        with open(file_path, "r") as file:
            csv_reader = csv.DictReader(file)
            data = list(csv_reader)

            # Store time and current data
            time_data = [float(row["Corrected time (s)"]) for row in data]
            raw_current_data = [float(row["WE(1).Current (A)"]) for row in data]
            self.data.append({
                "file": os.path.basename(file_path),
                "time": time_data,
                "raw_current": raw_current_data
            })

            # Calculate baseline slope
            baseline_start_time = 5  # Adjust as needed
            baseline_end_time = 20  # Adjust as needed
            baseline_data = [row for row in data if
                             baseline_start_time <= float(row["Corrected time (s)"]) <= baseline_end_time]
            baseline_slope = self.calculate_baseline_slope(baseline_data)

            # Correct raw current data
            corrected_current_data = self.correct_current(time_data, raw_current_data, baseline_slope)
            self.data[-1]["corrected_current"] = corrected_current_data

            # Find plateaus in the corrected current data
            plateau_indices = self.find_plateaus(corrected_current_data)
            self.data[-1]["plateau_indices"] = plateau_indices

            # Perform other analyses as needed
            # ...


if __name__ == "__main__":
    folder_path = r"C:\Users\olegolt\OneDrive - Norwegian University of Life Sciences\PhD\Boku\Experiments\Sensor\230829_NcAA9C_CN_0-800uM_XG_MOPS_pH7_30C"
    analyzer = RotatingDiskElectrodeAnalyzer(folder_path)
    analyzer.analyze_files()

    for entry in analyzer.data:
        print(f"File: {entry['file']}")
        print(f"Time data: {entry['time']}")
        print(f"Raw Current data: {entry['raw_current']}")
        print(f"Corrected Current data: {entry['corrected_current']}")


