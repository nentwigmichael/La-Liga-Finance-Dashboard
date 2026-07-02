import pandas as pd
import numpy as np

def calculate_kpis():
    # Load raw TM data
    df = pd.read_csv('data/raw/tm_data.csv', sep=';')
    
    # Sort data correctly to calculate YoY growth
    # Season format is "2015/16". We can extract start year to sort.
    df['Start_Year'] = df['Season'].apply(lambda x: int(x.split('/')[0]))
    df = df.sort_values(by=['Club', 'Start_Year']).reset_index(drop=True)
    
    # Calculate KPIs
    # 1. Nettotransferbilanz: Einnahmen - Ausgaben
    df['Net_Transfer_Balance'] = df['Transfer_Revenues'] - df['Transfer_Expenditures']
    
    # 2. Transfervolumen: Einnahmen + Ausgaben
    df['Total_Transfer_Activity'] = df['Transfer_Revenues'] + df['Transfer_Expenditures']
    
    # 3. YoY Squad Value Growth (Kaderwert-Wachstum)
    # Group by club and calculate percentage change. 
    # Use fillna(0) for the first year (2015/16) since there's no prior year.
    df['YoY_Squad_Value_Growth_%'] = df.groupby('Club')['Squad_Value_TM'].pct_change() * 100
    df['YoY_Squad_Value_Growth_%'] = df['YoY_Squad_Value_Growth_%'].fillna(0.0).round(2)
    
    # 4. Squad-Value to Transfer-Spend Ratio
    # Kaderwert / Transferausgaben
    # Avoid division by zero: if Transfer_Expenditures is 0, we can set it to NaN or a very high value.
    df['SV_to_Spend_Ratio'] = np.where(df['Transfer_Expenditures'] > 0,
                                       df['Squad_Value_TM'] / df['Transfer_Expenditures'],
                                       np.nan)
    df['SV_to_Spend_Ratio'] = df['SV_to_Spend_Ratio'].round(2)
    
    # Drop the temporary sorting column
    df = df.drop(columns=['Start_Year'])
    
    # Save the processed data
    output_path = 'data/processed/tm_processed_data.csv'
    df.to_csv(output_path, sep=';', index=False)
    print(f"Calculations completed. Processed data saved to {output_path}")

if __name__ == "__main__":
    calculate_kpis()
