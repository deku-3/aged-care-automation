import pandas as pd

# Load the service list file
service_df = pd.read_excel("data/Service-List-30-Jun-2024-Australia.xlsx")
service_df.columns = service_df.iloc[1] 
service_df =service_df[2:]
service_df = service_df.reset_index(drop=True)
# Step 1: Filter rows that are either Residential or Home Care
relevant_services = service_df[service_df["Care Type"].isin(["Residential Care", "Home Care"])]

# Step 2: Extract only needed columns
relevant_services = relevant_services[["Provider Name", "Suburb", "Postal Code"]]

# Step 3: Drop duplicates (unique combinations)
unique_provider_location = relevant_services.drop_duplicates().reset_index(drop=True)

# Step 4: Save to CSV for reference
unique_provider_location.to_csv("data/filtered_providers_for_compliance.csv", index=False)

print("✅ Saved filtered provider list to 'filtered_providers_for_compliance.csv'")