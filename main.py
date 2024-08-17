from fastapi import FastAPI, Query, HTTPException
import os
import shutil
import pandas as pd
from datetime import datetime
from load_env_data import csv_path
from Models.mainModels import PathModel
app = FastAPI(title="Relative Counter for Talha's Wedding")

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

async def create_file(name:str):
    try:
        mpath=os.path.join("data",name)
        PathModel(path=mpath)

    except Exception as e:
        return HTTPException(500,f"Error create file due to {e}")
    pass
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
                
                mdf = pd.read_csv(temp)
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
    new_number_of_member: int = Query(None, title="New total number of family members")
):
   
    
    # Read the existing CSV file into a DataFrame
    try:
        df = pd.read_csv(mcsvfp)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Data file not found")
    
    # Check if the DataFrame contains the specified guest_name
    if df[df['Relative_Name'].str.lower() == guest_name.lower()].empty:
        raise HTTPException(status_code=404, detail="Relative not found")
    
    # Update the record with the specified guest_name
    df.loc[df['Relative_Name'].str.lower() == guest_name.lower(), 'relation'] = new_relation if new_relation else df['relation']
    df.loc[df['Relative_Name'].str.lower() == guest_name.lower(), 'contact_info'] = new_contact_info if new_contact_info else df['contact_info']
    df.loc[df['Relative_Name'].str.lower() == guest_name.lower(), 'address'] = new_address if new_address else df['address']
    df.loc[df['Relative_Name'].str.lower() == guest_name.lower(), 'rsvp_status'] = new_rsvp_status if new_rsvp_status is not None else df['rsvp_status']
    df.loc[df['Relative_Name'].str.lower() == guest_name.lower(), 'number_of_member'] = new_number_of_member if new_number_of_member is not None else df['number_of_member']

    # Save the updated DataFrame back to the CSV file
    df.to_csv(mcsvfp, index=False)

    return {"message": "Record updated successfully!"}

@app.get("/get_data",name="Get user entry for dataframe",tags=['data manipulation'])
async def data_view(
    sort_by: str = Query(None, enum=["Relative_Name", "relation", "contact_info", "address", "rsvp_status", "number_of_member"], description="Column name to sort by"),
    ascending: bool = Query(True, description="Sort order, set to False for descending order"),
    page: int = Query(1, description="Page number", ge=1),
    size: int = Query(10, description="Number of records per page", ge=1)
):
    mdf = pd.read_csv(mcsvfp)

    # Sort the DataFrame if sort_by is provided
    if sort_by:
        mdf = mdf.sort_values(by=sort_by, ascending=ascending)

    # Calculate pagination details
    total_records = len(mdf)
    total_pages = (total_records // size) + (1 if total_records % size > 0 else 0)

    if page > total_pages:
        raise HTTPException(status_code=404, detail=f"Page {page} does not exist. Total pages: {total_pages}.")

    start_idx = (page - 1) * size
    end_idx = start_idx + size

    # Paginate the DataFrame
    mdf_paginated = mdf.iloc[start_idx:end_idx]

    # Convert the DataFrame to a list of dictionaries
    data = mdf_paginated.to_dict(orient="records")

    return {
        "page": page,
        "size": size,
        "total_records": total_records,
        "total_pages": total_pages,
        "data": data
    }

@app.delete("/delete_record",tags=['data manipulation'])
async def delete_record(guest_name: str):
    

    try:
        df = pd.read_csv(mcsvfp)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Data file not found")

    if df[df['Relative_Name'].str.lower() == guest_name.lower()].empty:
        raise HTTPException(status_code=404, detail="Relative not found")
    
    df = df[df['Relative_Name'].str.lower() != guest_name.lower()]


    df.to_csv(mcsvfp, index=False)

    return {"message": "Record deleted successfully!"}

@app.get("/counter",name="Count total guiests",description="Count total no of guests you call",tags=['counter'])

async def count_guests():
    cd=pd.read_csv(mcsvfp)
    tc = 0  
    for index, row in cd.iterrows():
        tc += row['number_of_member']   
    return {"Total guests are ":tc,"user_records":cd.to_dict(orient="records")}