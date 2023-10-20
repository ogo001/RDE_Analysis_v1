import os
import matplotlib.pyplot as plt
from analysis.data_processing import RotatingDiskElectrodeAnalyzer

class DataPlotter:
    def __init__(self, output_path):
        self.output_path = output_path

    def plot_data(self, current_data, time_data, filename):
        plt.figure()
        plt.plot(time_data, current_data)
        plt.xlabel("Corrected Time (s)")
        plt.ylabel("Current (A)")
        plt.title("Current vs Corrected Time")
        plt.grid(True)

        plot_path = os.path.join(self.output_path, filename)
        plt.savefig(plot_path)
        plt.close()

        print(f"Plot saved at: {plot_path}")

if __name__ == "__main__":
    output_path = r"/path/to/visualization/directory"
    analyzer = RotatingDiskElectrodeAnalyzer(folder_path)  # Provide the correct folder_path here
    data_collection = analyzer.analyze_files()

    plotter = DataPlotter(output_path)

    for file_data in data_collection:
        current_data = [float(row["WE(1).Current (A)"]) for row in file_data]
        time_data = [float(row["Corrected time (s)"]) for row in file_data]

        filename = os.path.basename(file_data).replace(".csv", "_plot.png")
        plotter.plot_data(current_data, time_data, filename)
