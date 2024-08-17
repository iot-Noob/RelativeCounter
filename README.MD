# Relative Counter for Weeding

## Overview

This FastAPI application manages and processes CSV files containing guest information for an event. It supports creating, updating, viewing, and deleting guest records. The application also provides endpoints to handle multiple CSV files, count total guests, and manage guest data efficiently.

## Features

- **Create CSV Files**: Create new CSV files to store guest data.
- **Get List of Files**: Retrieve a list of all CSV files.
- **Delete CSV Files**: Delete existing CSV files.
- **Add Data**: Add new guest data to a specified CSV file.
- **Edit Data**: Update existing guest data in a CSV file.
- **View Data**: Retrieve and paginate guest data from CSV files.
- **Delete Record**: Remove a guest record from a CSV file.
- **Count Guests**: Calculate the total number of guests across multiple CSV files.

## Setup

1. **Clone the Repository**

   ```bash
   git clone https://github.com/iot-Noob/RelativeCounter/tree/main
   ```
### 2. Navigate to the Project Directory
   
```
cd RelativeCounter
```

### 3. Install Dependencies

Ensure you have Python 3.7+ installed. Create a virtual environment and install the required packages.

```bash
python -m venv env
source env/bin/activate  # On Windows use `env\Scripts\activate`
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

Create a .env file in the root directory with the following content:

```env
CSV_PATH=./data/relative_counter.csv
```
### 5. Run the app

```bash
 uvicorn main:app --reload
```

The application will be available at http://127.0.0.1:8000.

 
