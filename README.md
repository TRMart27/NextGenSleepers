# Clustering Draft Prospects to Identify Undervalued Players

This project collects, parses, and analyzes NFL draft prospect data to identify players who may be undervalued based on clustering analysis.  
The goal is to find patterns in performance and biographical data that traditional scouting might overlook.

## Features
- **Automated Data Collection**  
  Scrapers pull player stats and bio data from various sources (College Football Data API, Pro Football Reference, etc.).
  
- **Data Parsing & Cleaning**  
  Custom parsers structure raw HTML/JSON into usable datasets.
  
- **Database Support**  
  Data is cached and stored locally using SQLite for repeatable analysis.
  
- **Position-Specific Models**  
  Models are tailored to different positions (QB, WR, etc.) to improve clustering accuracy.

- **Clustering Analysis**  
  Groups similar players to highlight potential draft steals.

## Project Structure


## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/TRMart27/NextGenSleepers.git
   cd NextGenSleepers
   
2. Install Dependencies:
    ```bash
   pip install -r requirements.txt

3. Set up Configurations in config.py (API keys, Data paths, etc)

## Usage



## Future Improvements 
