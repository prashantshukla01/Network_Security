import os
import sys
import json
import ssl

from dotenv import load_dotenv
load_dotenv()

MONGO_DB_URL=os.getenv("MONGO_DB_URL")
print(MONGO_DB_URL)

import certifi
ca=certifi.where()

import pandas as pd
import numpy as np
import pymongo
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

class NetworkDataExtract():
    def __init__(self):
        try:
            pass
        except Exception as e:
            raise NetworkSecurityException(e,sys)
        
    def csv_to_json_convertor(self,file_path):
        try:
            data=pd.read_csv(file_path)
            data.reset_index(drop=True,inplace=True)
            records=list(json.loads(data.T.to_json()).values())
            return records
        except Exception as e:
            raise NetworkSecurityException(e,sys)
        
    def insert_data_mongodb(self,records,database,collection):
        try:
            self.database=database
            self.collection=collection
            self.records=records

            print("Attempting to connect to MongoDB Atlas...")
            
            # Get connection string from environment
            connection_string = MONGO_DB_URL
            
            # Print connection string with hidden password for debugging
            if connection_string and "@" in connection_string:
                parts = connection_string.split("@")
                auth = parts[0].split("://")[1]
                username = auth.split(":")[0]
                masked_conn = connection_string.replace(auth, f"{username}:********")
                print(f"Using connection string: {masked_conn}")
            
            # Most reliable connection approach for Atlas
            self.mongo_client = pymongo.MongoClient(
                connection_string,
                ssl=True,
                tlsAllowInvalidCertificates=True,
                serverSelectionTimeoutMS=30000
            )
            
            # Test the connection
            print("Testing connection...")
            self.mongo_client.admin.command('ping')
            print("Connected successfully to MongoDB Atlas!")
            
            self.database = self.mongo_client[self.database]
            self.collection = self.database[self.collection]
            
            print(f"Inserting {len(self.records)} records...")
            
            # Check if collection has data and drop it to avoid duplicates (User Request)
            if self.collection.count_documents({}) > 0:
                print("Collection already exists. Dropping to ensure unique dataset...")
                self.collection.drop()
                print("Collection dropped.")
                
            self.collection.insert_many(self.records)
            print("Data inserted successfully!")
            return(len(self.records))
        except Exception as e:
            print(f"MongoDB connection error: {str(e)}")
            print("\nTroubleshooting suggestions:")
            print("1. Check if your MongoDB Atlas cluster is running")
            print("2. Verify your IP address is whitelisted in MongoDB Atlas")
            print("3. Check username and password in your connection string")
            print("4. Try connecting from a different network")
            print("5. If using a VPN, try disconnecting from it")
            print("6. Consider using MongoDB Compass as an alternative")
            raise NetworkSecurityException(e,sys)
        
if __name__=='__main__':
    FILE_PATH="Network_Data/phisingData.csv"
    DATABASE="PrashantAI"
    Collection="NetworkData"
    networkobj=NetworkDataExtract()
    records=networkobj.csv_to_json_convertor(file_path=FILE_PATH)
    print(records)
    no_of_records=networkobj.insert_data_mongodb(records,DATABASE,Collection)
    print(no_of_records)
        


