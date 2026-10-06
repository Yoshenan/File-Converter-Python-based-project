import numpy as np
import pandas as pd

def generate_messy_dataset(filename: str = "dirty_dataset.csv", rows: int = 20) -> pd.DataFrame:
    np.random.seed(42)

    messy_data = {
        # Raw Column Names (Dirty spaces, special chars, mixed casing)
        ' Contact Email! ': [
            'USER1@Gmail.com', 'invalid_email.com', '  john.doe@yahoo.com ', 
            'no_at_symbol', None, 'ALICE@Domain.org', 'test@@extra.com', 
            'SUPPORT@COMPANY.CO', '   ', 'clean@test.com'
        ] * (rows // 10),

        'Phone Number#': [
            '+1 (555) 019-2834', '123-456-7890', 'n/a', '  555.987.6543 ', 
            '', 'INVALID_PHONE', '+44 20 7946 0912', '5551112222', None, '00000'
        ] * (rows // 10),

        'Full Address': [
            '123 Main St, Apt 4B, New York, NY 10001',
            '456 Oak Ave, Austin TX 78701',
            '789 Pine Rd, Suite 200, Chicago, IL 60611',
            '101 Maple Drive',                      # Single part (no comma)
            '   ',                                 # Empty
            '55 Broadway, New York, NY',           # No ZIP
            '12 First St, Sunset Bay, CA 90210',
            '999 Cedar Ln, Miami, FL 33101',
            '404 Error Rd, Lost City',             # 2 parts
            '777 Lucky Blvd, Apt 7, Vegas, NV 89109'
        ] * (rows // 10),

        'Item Weight': [
            '75.5 kg', ' 80kg ', '72.0 kg', '150.2 lbs', '90.5KG', 
            'INVALID', '68.4 kg', '   ', '110 lbs', '85.0 kg'
        ] * (rows // 10),

        'Reading Score': [
            15.0, 18.0, 14.5, 500.0, 16.2,         # 500.0 is a Z-score outlier
            17.1, 15.8, -999.0, 14.9, 16.0         # -999.0 is an outlier
        ] * (rows // 10),

        ' Constant Col ': ['SAME_VALUE'] * rows,    # Uninformative column
        ' Null Col ': [None] * rows                 # 100% missing column
    }

    df = pd.DataFrame(messy_data)
    df.to_csv(filename, index=False)
    print(f"Messy dataset successfully generated and saved to '{filename}'!")
    return df

# Generate the file
if __name__ == "__main__":
    generate_messy_dataset("dirty_dataset.csv", rows=20)