import pandas as pd
from rapidfuzz import process, fuzz

# Load both sheets
service_df = pd.read_excel("data/Service-List-30-Jun-2024-Australia.xlsx")
service_df.columns = service_df.iloc[1] 
service_df =service_df[2:]
service_df = service_df.reset_index(drop=True)
ratings_df=pd.read_excel('data/star-ratings-quarterly-data-extract-may-2025_0.xlsx',sheet_name=1)

# Filter residential care only
residential_services = service_df[service_df["Care Type"].str.contains("Residential", case=False)].copy()

# Prepare a column to match on
residential_services["Match Key"] = (
    residential_services["Service Name"].str.lower().str.strip() + " - " +
    residential_services["Provider Name"].str.lower().str.strip() + " - " +
    residential_services["Suburb"].str.lower().str.strip()
)

ratings_df["Match Key"] = (
    ratings_df["Service Name"].str.lower().str.strip() + " - " +
    ratings_df["Provider Name"].str.lower().str.strip() + " - " +
    ratings_df["Service Suburb"].str.lower().str.strip()
)

# Create dictionary from star rating file for quick lookup
rating_dict = dict(zip(ratings_df["Match Key"], ratings_df.to_dict("records")))

# Define matching function
def match_rating(row):
    match, score, _ = process.extractOne(
        row["Match Key"],
        rating_dict.keys(),
        scorer=fuzz.token_sort_ratio
    )
    if score >= 90:  # Adjust threshold as needed
        return rating_dict[match]
    return None

# Apply fuzzy matching
residential_services["Rating Match"] = residential_services.apply(match_rating, axis=1)

# Extract desired columns from match
rating_cols = ["Overall Star Rating", "Residents' Experience rating", "Compliance rating", "Staffing rating", "Quality Measures rating"]
for col in rating_cols:
    residential_services[col] = residential_services["Rating Match"].apply(lambda x: x.get(col) if x else None)

# Drop helper columns
residential_services.drop(columns=["Match Key", "Rating Match"], inplace=True)

# Save output
residential_services.to_csv("residential_services_with_star_ratings.csv", index=False)
print("✅ Output saved as 'residential_services_with_star_ratings.csv'")
