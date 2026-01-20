from flask import Flask, request, render_template, send_file
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import io
import os

app = Flask(__name__)

# Acceptable temperature ranges
lower_bound = 18.0
upper_bound = 22.0

# Configure matplotlib for dark theme
plt.style.use('dark_background')
plt.rcParams.update({
    'figure.facecolor': '#1e293b',
    'axes.facecolor': '#0f172a',
    'axes.edgecolor': '#334155',
    'axes.labelcolor': '#94a3b8',
    'text.color': '#f1f5f9',
    'xtick.color': '#94a3b8',
    'ytick.color': '#94a3b8',
    'grid.color': '#334155',
    'grid.alpha': 0.5,
    'legend.facecolor': '#1e293b',
    'legend.edgecolor': '#334155',
    'font.family': 'sans-serif',
    'font.size': 10,
})

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file part", 410
    
    file = request.files['file']
    
    if file.filename == '':
        return "No selected file", 420

    if file and allowed_file(file.filename):
        try:
            # Read the file into a DataFrame
            df = pd.read_csv(file, encoding='latin1')

            # Check if required columns exist
            required_columns = ['Time', 'Celsius(C)']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                return f"Missing required columns: {', '.join(missing_columns)}", 400

            # Handle the Serial Number column if it's missing for subsequent rows
            if 'Serial Number' in df.columns:
                # Fill missing serial numbers with the first row's serial number
                df['Serial Number'] = df['Serial Number'].fillna(df['Serial Number'].iloc[0])
            else:
                # If there's no 'Serial Number' column, create it based on the first row
                df['Serial Number'] = df.iloc[0, -1]  # Assuming the serial number is in the last column

            # Convert 'Celsius(C)' to numeric values and 'Time' to datetime
            df['Celsius(C)'] = pd.to_numeric(df['Celsius(C)'], errors='coerce')
            df['Time'] = pd.to_datetime(df['Time'], errors='coerce')

            # Drop rows with NaN values
            df = df.dropna()

            # Filter data based on the provided time range
            start_time = request.form.get('start_time')
            end_time = request.form.get('end_time')
            
            if start_time:
                df = df[df['Time'] >= pd.to_datetime(start_time)]
            if end_time:
                df = df[df['Time'] <= pd.to_datetime(end_time)]

            if df.empty:
                return "No data available for the selected time range.", 430

            # Check if the temperature is within the acceptable range
            df['Within Range'] = df['Celsius(C)'].between(lower_bound, upper_bound)
            
            # Create the plot with modern styling
            fig, ax = plt.subplots(figsize=(12, 6), dpi=100)
            
            # Plot the main temperature line
            ax.plot(df['Time'], df['Celsius(C)'], 
                   color='#3b82f6', linewidth=2, alpha=0.8, label='Temperature')
            
            # Fill the acceptable range area
            ax.fill_between(df['Time'], lower_bound, upper_bound, 
                           color='#10b981', alpha=0.15, label='Acceptable Range (18-22°C)')
            
            # Plot points within range (green)
            within_range = df[df['Within Range']]
            ax.scatter(within_range['Time'], within_range['Celsius(C)'], 
                      color='#22c55e', s=50, zorder=5, label='Within Range', edgecolors='white', linewidth=0.5)
            
            # Plot points outside range (red)
            outside_range = df[~df['Within Range']]
            ax.scatter(outside_range['Time'], outside_range['Celsius(C)'], 
                      color='#ef4444', s=50, zorder=5, label='Outside Range', edgecolors='white', linewidth=0.5)
            
            # Add horizontal lines for bounds
            ax.axhline(y=lower_bound, color='#10b981', linestyle='--', alpha=0.5, linewidth=1)
            ax.axhline(y=upper_bound, color='#10b981', linestyle='--', alpha=0.5, linewidth=1)
            
            # Styling
            ax.set_xlabel('Time', fontsize=12, fontweight='500', labelpad=10)
            ax.set_ylabel('Temperature (°C)', fontsize=12, fontweight='500', labelpad=10)
            ax.set_title('Temperature Readings Analysis', fontsize=16, fontweight='600', pad=20, color='#f1f5f9')
            
            # Grid
            ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
            
            # Legend
            ax.legend(loc='upper right', framealpha=0.9, fontsize=9)
            
            # Rotate x-axis labels
            plt.xticks(rotation=45, ha='right')
            
            # Add some statistics as text
            stats_text = f'Min: {df["Celsius(C)"].min():.1f}°C | Max: {df["Celsius(C)"].max():.1f}°C | Avg: {df["Celsius(C)"].mean():.1f}°C'
            fig.text(0.5, 0.02, stats_text, ha='center', fontsize=10, color='#94a3b8', 
                    bbox=dict(boxstyle='round,pad=0.5', facecolor='#1e293b', edgecolor='#334155'))
            
            plt.tight_layout(rect=[0, 0.05, 1, 1])
            
            img = io.BytesIO()
            fig.savefig(img, format='png', facecolor='#1e293b', edgecolor='none', bbox_inches='tight')
            img.seek(0)
            plt.close(fig)
            
            return send_file(img, mimetype='image/png', as_attachment=True, download_name='plot.png')
        
        except pd.errors.EmptyDataError:
            return "Uploaded file is empty", 440
        except pd.errors.ParserError:
            return "Error parsing the file. Ensure it is in CSV format", 450
        except Exception as e:
            return f"An error occurred: {e}", 500
    else:
        return "Invalid file type. Please upload a CSV file.", 460

def allowed_file(filename):
    """Check if the file extension is allowed."""
    ALLOWED_EXTENSIONS = {'csv', 'txt'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5500, debug=True)
