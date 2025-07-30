import pandas as pd

# Load the service list Excel
df = pd.read_excel("data/Service-List-30-Jun-2024-Australia.xlsx")
df.columns = df.iloc[1] 
df =df[2:]
df = df.reset_index(drop=True)
# Normalize 'Care Type' column (remove leading/trailing spaces)
df["Care Type"] = df["Care Type"].str.strip().str.lower()

# Filter for Home Care and Residential services only
filtered_df = df[df["Care Type"].isin(["home care", "residential"])]
print(f"Filtered down to {len(filtered_df)} rows with Home Care or Residential services.")

# Get unique provider names
unique_providers = filtered_df["Provider Name"].dropna().unique()
print(f"Found {len(unique_providers)} unique providers.")
pd.DataFrame(unique_providers, columns=["Provider Name"]).to_csv('data/unique_providers.csv', index=False)