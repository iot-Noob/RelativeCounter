from fastapi import FastAPI, Query, HTTPException 
import os
import shutil
import pandas as pd
from datetime import datetime
from load_env_data import csv_path
from Models.mainModels import PathModel
from enum import Enum
from typing import List
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI(title="Relative Counter for Talha's Wedding")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow requests from any origin
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

mcsvfp=csv_path if csv_path else "./data/relative_counter.csv"

@app.on_event("startup")
async def startup_event():

    if not os.path.exists(mcsvfp):
        sp=os.path.split(mcsvfp)
        if not os.path.exists(sp[0]):
            os.makedirs(sp[0])
        mdf = pd.DataFrame(columns=["entry_date_time", "Relative_Name", "relation", "contact_info", "address", "rsvp_status", "number_of_member"])
        mdf.to_csv(mcsvfp, index=False)

@app.post("/create_file",name="create a new csv file for data entry",description="Create seprate csv for each set of users re;ative you wnat ot count sepratly",tags=['file_creation'])

async def create_file(name:str ):
    try:
        mpath=os.path.join("data",name)
        PathModel(path=mpath)
        if os.path.exists(mpath):
            return HTTPException(500,f"File already exists name {name}")
        mdf = pd.DataFrame(columns=["entry_date_time", "Relative_Name", "relation", "contact_info", "address", "rsvp_status", "number_of_member"])
        mdf.to_csv(mpath, index=False)
        return {"file creation sucess"}
    except Exception as e:
        return HTTPException(500,f"Error create file due to {e}")

@app.get("/get_files",name="get list of all csv files",description="all seprate csv file for different users",tags=['file_creation'])
async def get_files():
    root_path=os.path.split(mcsvfp)
    mr=[]
    for root,_,file in os.walk(root_path[0]):
        
            for ind,f in enumerate(file):
                if f.endswith(".csv"):
                    mr.append({"index":ind,"filename":f})
            return mr
 
@app.delete("/delete_file",name="create a new csv file to delete",description="delete csv ",tags=['file_creation'])

async def delete_csv(path:str=Query(...,description="Delete file path")):
    try:
        temp=os.path.join("data",path)
        PathModel(path=temp)
        if not os.path.exists(temp):
            return  HTTPException(400,"fILE NOT FOUND")
        else:
      
            os.remove(temp)
    except Exception as e:
        return HTTPException(500,f"Error occur deletion csv {e}")
@app.post("/add_data", description="Input relative list", tags=['data manipulation'])
async def add_data(
    relative_name: str = Query(..., title="Relative name", description="Name of your relative"),
    relation: str = Query(..., title="Your relation to relative"),
    contact_info: str = Query(..., title="Phone number of relative or email"),
    address: str = Query(..., title="Address of relative"),
    rsvp_status: bool = Query(..., title="RSVP status", description="Confirm if relative is coming or not"),
    number_of_member: int = Query(..., title="Total number of family members of relative", description="Total number of family members of the current relative you are calling."),
    file_name:str=Query(None,title="Name of csv file",description="Name of csv file you wnat  to work on e.g. relative.csv store data sepratly in csv file name you mention")
):
    try:
       
        if file_name:
            temp=os.path.join("data",file_name)
            PathModel(path=temp)
            if not os.path.exists(temp):
                return  HTTPException(400,"fILE NOT FOUND")
            else:
                mcsvfp=temp
        else:
            mcsvfp=csv_path if csv_path else "./data/relative_counter.csv"
        # Read the existing CSV file into a DataFrame
        
        mdf = pd.read_csv(mcsvfp)

        # Check if the relative's name already exists
        if not mdf[mdf["Relative_Name"].str.lower() == relative_name.lower()].empty:
            raise HTTPException(status_code=400, detail="Error: Relative name already exists")

        # Create a new DataFrame from the input data
        data = {
            "entry_date_time": datetime.now().isoformat(),  # Use current date and time in ISO format
            "Relative_Name": relative_name,
            "relation": relation,
            "contact_info": contact_info,
            "address": address,
            "rsvp_status": rsvp_status,
            "number_of_member": number_of_member
        }
        nd = pd.DataFrame([data])

        # Append the new data to the existing DataFrame
        mdf = pd.concat([mdf, nd], ignore_index=True)

        # Save the updated DataFrame back to the CSV file
        mdf.to_csv(mcsvfp, index=False)

        return {"message": "Data added successfully!"}
    except Exception as e:
        return HTTPException(400,f"Error save csv due to {e}")
    
@app.post("/edit_data",tags=['data manipulation'])
async def edit_record(
    guest_name: str = Query(..., title="Relative name", description="Name of the relative to update"),
    new_relative_name: str = Query(None, title="New relative name"),
    new_relation: str = Query(None, title="New relation to relative"),
    new_contact_info: str = Query(None, title="New phone number of relative or email"),
    new_address: str = Query(None, title="New address of relative"),
    new_rsvp_status: bool = Query(None, title="New RSVP status"),
    new_number_of_member: int = Query(None, title="New total number of family members"),
    file_name: str = Query(None, title="Name of csv file", description="Name of csv file you want to work on e.g. relative.csv store data separately in csv file name you mention")
):
    try:
        # Determine the file path to use
        if file_name:
            file_path = os.path.join("data", file_name)
            PathModel(path=file_path)
            if not os.path.exists(file_path):
                raise HTTPException(status_code=400, detail="File not found")
            mcsvfp = file_path
        else:
            mcsvfp = csv_path if csv_path else "./data/relative_counter.csv"
        
        # Read the existing CSV file into a DataFrame
        df = pd.read_csv(mcsvfp)

        # Check if the DataFrame contains the specified guest_name
        guest_exists = not df[df['Relative_Name'].str.lower() == guest_name.lower()].empty
        if not guest_exists:
            raise HTTPException(status_code=404, detail="Relative not found")
        
        # Update the record with the specified guest_name
        if new_relative_name:
            df.loc[df['Relative_Name'].str.lower() == guest_name.lower(), 'Relative_Name'] = new_relative_name
        if new_relation:
            df.loc[df['Relative_Name'].str.lower() == guest_name.lower(), 'relation'] = new_relation
        if new_contact_info:
            df.loc[df['Relative_Name'].str.lower() == guest_name.lower(), 'contact_info'] = new_contact_info
        if new_address:
            df.loc[df['Relative_Name'].str.lower() == guest_name.lower(), 'address'] = new_address
        if new_rsvp_status is not None:
            df.loc[df['Relative_Name'].str.lower() == guest_name.lower(), 'rsvp_status'] = new_rsvp_status
        if new_number_of_member is not None:
            df.loc[df['Relative_Name'].str.lower() == guest_name.lower(), 'number_of_member'] = new_number_of_member

        # Save the updated DataFrame back to the CSV file
        df.to_csv(mcsvfp, index=False)

        return {"message": "Record updated successfully!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cannot edit data due to: {e}")
    
@app.get("/get_data",name="Get user entry for dataframe",tags=['data manipulation'])
async def data_view(
    file_name: List[str] = Query(None, title="Name of CSV files", description="List of CSV files to process"),
    sort_by: str = Query(None, enum=["Relative_Name", "relation", "contact_info", "address", "rsvp_status", "number_of_member"], description="Column name to sort by"),
    ascending: bool = Query(True, description="Sort order, set to False for descending order")
):
    try:
        all_data = {}  # This will store the combined data from all files

        if file_name and len(file_name) > 0:
            for fname in file_name:
                file_path = os.path.join("data", fname)
                
                if not os.path.exists(file_path):
                    raise HTTPException(status_code=400, detail=f"File not found: {fname}")

                # Read the CSV file
                df = pd.read_csv(file_path)
      
                # Sort the DataFrame if sort_by is provided
                if sort_by:
                    if sort_by not in df.columns:
                        raise HTTPException(status_code=400, detail=f"Invalid sort_by column: {sort_by}")
                    df = df.sort_values(by=sort_by, ascending=ascending)
                
                # Add the data under the filename as the key
                all_data[fname] = df.to_dict(orient="records")
            
        else:
            # Default CSV file processing
            file_path = "./data/relative_records.csv"
            if not os.path.exists(file_path):
                raise HTTPException(status_code=400, detail="Default CSV file not found")

            df = pd.read_csv(file_path)
            
            # Sort the DataFrame if sort_by is provided
            if sort_by:
                if sort_by not in df.columns:
                    raise HTTPException(status_code=400, detail=f"Invalid sort_by column: {sort_by}")
                df = df.sort_values(by=sort_by, ascending=ascending)
            
            # Add the data under the filename as the key
            all_data["relative_records.csv"] = df.to_dict(orient="records")

        return {"total_records": sum(len(data) for data in all_data.values()), "data": all_data}

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading file due to {e}")
    
@app.delete("/delete_record",tags=['data manipulation'])
async def delete_record(guest_name: str, file_name: str = Query(None, title="Name of csv file", description="Name of csv file you want to work on e.g. relative.csv store data separately in csv file name you mention")):
     
    try:
        if file_name:
            file_path = os.path.join("data", file_name)
            PathModel(path=file_path)
            if not os.path.exists(file_path):
                raise HTTPException(status_code=400, detail="File not found")
            mcsvfp = file_path
        else:
            mcsvfp = csv_path if csv_path else "./data/relative_counter.csv"

        df = pd.read_csv(mcsvfp)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Data file not found")

    if df[df['Relative_Name'].str.lower() == guest_name.lower()].empty:
        raise HTTPException(status_code=404, detail="Relative not found")
    
    df = df[df['Relative_Name'].str.lower() != guest_name.lower()]


    df.to_csv(mcsvfp, index=False)

    return {"message": "Record deleted successfully!"}

@app.get("/counter",name="Count total guiests",description="Count total no of guests you call",tags=['counter'])

async def count_guests(
    file_name: List[str] = Query(..., title="Name of CSV files", description="List of CSV files to process")
):
    total_guests = 0
    file_data = {}
    
    for name in file_name:
        file_path = os.path.join("data", name)
        PathModel(path=file_path)
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=400, detail=f"File not found: {name}")
        
        # Read the CSV file
        df = pd.read_csv(file_path)
        
        # Ensure 'number_of_member' column exists
        if 'number_of_member' not in df.columns:
            raise HTTPException(status_code=400, detail=f"'number_of_member' column not found in file: {name}")
        
        # Calculate total guests for this file
        file_total = df['number_of_member'].sum()
        total_guests += file_total
        
        # Convert DataFrame to a dictionary with standard Python types
        file_data[name] = {
            "total_guests": int(file_total),  # Convert numpy.int64 to int
            "user_records": df.to_dict(orient="records")
        }
    
    # Convert total_guests to int to ensure compatibility
    return {
        "total_guests": int(total_guests),  # Convert numpy.int64 to int
        "files_data": file_data
    }