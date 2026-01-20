..
-EasyPlot is a web application developed using Flask that allows users to upload CSV files containing temperature readings.
The application generates a plot visualizing the temperature data, highlighting areas where the temperature falls within a specified range.
Users can also specify a time range for filtering the data before generating the plot.
This project was developed as part of a university course to demonstrate proficiency in web development with Flask, data processing with Pandas, and visualization with Matplotlib.
-

-Features:
File Upload: Users can upload CSV files containing temperature data.
Time Range Filtering: Users can specify a time range to filter the data.
Temperature Range Highlighting: The plot highlights temperature readings that fall within a predefined acceptable range.
Error Handling: The application provides meaningful error messages for incorrect file formats or missing data.
-

-Tech Used:
Web Framework : Flask
Data Manipulation and Analysis : Pandas
Plotting Library : Matplotlib
UI : HTML , CSS
-

-To run this project locally:
Clone the Repo --> git clone https://github.com/GiannisMand/EasyPlot.git
Create a Virtual Enviroment
Install Required Packages --> pip install -r requirements.txt
Run The Flask Application --> python app.py
Build Docker Image --> docker build -t (your-image-name)
Run The Docker Container --> docker run -p 5500:5500 (your-image-name)
The application will be accessible at http://127.0.0.1:5500 by default
-

-Error Handling
The various error scenarios are being handled by the application:
File not Provided --> Returns a 410 error 
Invalid File Type --> Returns a 460 error
Missing Columns   --> Returns a 400 error 
Empty File        --> Returns a 440 error
Parsing Errors    --> Returns a 450 error
-
