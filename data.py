import os
import sqlite3
import pandas as pd
import yaml
import re
import num2words
import numpy as np

def convert_data(user_input, output_user):
    _, user = os.path.splitext(user_input.lower())
    _, output = os.path.splitext(output_user.lower())

    try:
        # READ INPUT
        if user == ".csv":
            df = pd.read_csv(user_input)
        elif user == ".json":
            df = pd.read_json(user_input)
        elif user in [".xls", ".xlsx", ".odf", ".odt", ".ods", ".xlsm", ".xlsb"]:
            df = pd.read_excel(user_input)
        elif user in [".db", ".sqlite", ".sql"]:
            conn = sqlite3.connect(user_input)
            sql_query = input("Enter SQL query (or press Enter for whole table): ").strip()
            if not sql_query:
                table_name = input("Enter table name: ").strip()
                sql_query = f"SELECT * FROM {table_name}"
            df = pd.read_sql_query(sql_query, conn)
            conn.close()
        elif user in [".parquet", ".pq"]:
            df = pd.read_parquet(user_input)
        elif user in [".yaml", ".yml"]:
            with open(user_input, "r", encoding="utf-8") as f:
                raw_data = yaml.safe_load(f)
            df = pd.DataFrame(raw_data)
        elif user == ".html":
            df = pd.read_html(user_input)[0]
        else:
            print(f"Unsupported input format: {user}")
            return

        # WRITE OUTPUT
        if output == ".csv":
            df.to_csv(output_user, index=False)
        elif output in [".xls", ".xlsx", ".odf", ".odt", ".ods", ".xlsm", ".xlsb"]:
            df.to_excel(output_user, index=False)
        elif output == ".json":
            df.to_json(output_user, orient="records", indent=4)
        elif output in [".parquet", ".pq"]:
            df.to_parquet(output_user, index=False)
        elif output in [".yaml", ".yml"]:
            data_dict = df.to_dict(orient="records")
            with open(output_user, "w", encoding="utf-8") as f:
                yaml.dump(data_dict, f, default_flow_style=False)
        elif output == ".html":
            df.to_html(output_user, index=False)
        elif output in [".db", ".sqlite", ".sql"]:
            table_name = input("Enter target table name to create/replace: ").strip()
            conn = sqlite3.connect(output_user)
            df.to_sql(table_name, conn, index=False, if_exists="replace")
            conn.close()
        else:
            print(f"Unsupported output format: {output}")
            return

        print(f"Saved: {output_user}")

    except FileNotFoundError:
        print(f"File not found: {user_input}")
    except Exception as e:
        print(f"Error processing data: {e}")


def clean_columns(df:pd.DataFrame)-> pd.DataFrame:
    df = df.copy()
    clean_func = lambda x: (
                            num2words(x) if isinstance(x,(int,float))  
                                else re.sub(r'\d+',
                                lambda m : num2words(int(m.group())),
                                re.sub(r"[()€$]",'',str(x)).lower().strip()
                                )
    )
    df.columns = df.columns.map(clean_func)
    return df

def normalize_text(df:pd.DataFrame, fill_value: str = "unknown")-> pd.DataFrame:
    df = df.copy()
    text_cols = df.select_dtypes(include=["object"]).columns

    for col in text_cols:

        df[col].notna()
        df[col] = df[col].astype(str).str.strip().str.lower()
        df[col]= df[col].astype(str).str.normalize("NFKD").str.encode("ascii", "ignore").str.decode("utf-8")
        df[col] = df[col].str.replace(r'[^a-zA-Z0-9\s]','',regex=True)
        df[col] = df[col].fillna(fill_value)

    return df
        

def drop_uninformative_columns(df: pd.DataFrame, missing_threshold: float = 0.9) -> pd.DataFrame:
    """Drops columns with mostly missing values (>90%) or only a single unique value."""
    df = df.copy()
    
    # 1. Drop columns exceeding missing value threshold
    too_many_nulls = df.columns[df.isnull().mean() > missing_threshold]
    
    # 2. Drop zero-variance columns (only 1 unique value)
    zero_variance = [col for col in df.columns if df[col].nunique(dropna=True) <= 1]
    
    cols_to_drop = list(set(too_many_nulls).union(set(zero_variance)))
    if cols_to_drop:
        print(f"Dropping uninformative columns: {cols_to_drop}")
        df = df.drop(columns=cols_to_drop)
        
    return df

def convert_types(df: pd.DataFrame, threshold: float = 0.8 )->pd.DataFrame:
    df = df.copy()
    bool_map = {'true': True, 't': True, 'yes': True, 'y': True, '1': True,
               'false': False, 'f': False, 'no': False, 'n': False, '0': False}

    for col in df.select_dtypes(include=['object','string']).columns:
        s_clean = df[col].dropna().astype(str).str.strip().str.lower()

        if s_clean.empty:
            continue
        if set(s_clean.unique()).issubset(bool_map.keys()):
            df[col] =s_clean.map(bool_map)
            continue

        dates = pd.to_datetime(df[col],errors='coerce',format='mixed')
        if(dates.notna().sum()/len(s_clean)) >= threshold:
            df[col] = dates
            continue

        nums_str = df[col].astype(str).str.replace(r'[\$,€,£,¥,%,]', '', regex=True)
        nums = pd.to_numeric(nums_str,errors='coerce')
        if(nums.notna().sum()/len(s_clean)) >= threshold:
            df[col] = nums.astype('Int64') if (nums.dropna()%1 == 0 ).all() else  nums


    return df

def optimize(df:pd.DataFrame,threshold : float = 0.5)-> pd.DataFrame:
    df = df.copy()
    for col in df.select_dtypes(include=['object','string']).columns:
        if df[col].nunique(dropna=True)/max(1,len(df))<threshold:
            df[col] =df[col].astype('category')

    return df

def validation(df: pd.DataFrame, outlier_z_threshold: float = 3.0) -> pd.DataFrame:
    df = df.copy()

    # 1. PHONE & EMAIL CLEANING
    for col in df.columns:
        col_clean = col.lower().strip()
        
        # Phone Cleaning (Removes non-digit characters except leading '+')
        if any(keyword in col_clean for keyword in ['phone', 'mobile', 'fax', 'phone_num']):
            s = df[col].astype(str).str.replace(r'[^\d+]', '', regex=True)
            df[col] = s.replace(r'^\s*$', np.nan, regex=True)
            
        # Email Validation (Keeps valid emails, sets invalid ones to NaN)
        elif any(keyword in col_clean for keyword in ['email_address', 'gmail', 'email', 'mail']):
            pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            s = df[col].astype(str).str.strip().str.lower()
            df[col] = s.where(s.str.match(pattern, na=False), np.nan)

        elif any(keyword in col_clean for keyword in ['addr','address','location','street']):
            
            def split_addr(x):
                if pd.isna(x) or str(x).strip().lower() in ['nan', 'none', '']:
                    return ['', '', '']
                s = str(x).strip()
                return s.rsplit(',', 2) if ',' in s else s.rsplit(' ', 2)
            s= df[col].astype(str).apply(split_addr).apply(pd.Series)

            if s.shape[1]==1:
              s[1]=''
              s[2] =''
            elif s.shape[1]==2:
               s[2] = s[1]
               s[1] = ''
            
            df[f"{col}_street"] = s[0].str.strip().str.title().fillna('')
            df[f"{col}_city"] = s[1].str.strip().fillna('')
            df[f"{col}_state_zip"] = s[2].str.strip().fillna('')


    # 2. MEDIAN OUTLIER IMPUTER
    for col in df.select_dtypes(include=[np.number]).columns:
        std = df[col].std()
        if std > 0:
            median_val = df[col].median()
            z_scores = (df[col] - df[col].mean()).abs() / std
            df.loc[z_scores > outlier_z_threshold, col] = median_val

    # 3. NUMBER & UNIT SPLITTER
    UNIT_PATTERN = r'^\s*([+-]?\d+(?:\.\d+)?)\s*(kg|lbs|g|mg|cm|m|km|oz|lb|l|ml|gb|tb|mb)$'
    text_cols = df.select_dtypes(include=['object', 'string']).columns
    
    for col in text_cols:
        col_clean = col.lower().strip()
        # Skip contact and address columns completely!
        if any(kw in col_clean for kw in ['addr', 'address', 'location', 'street', 'phone', 'email', 'city', 'state', 'zip']):
            continue
            
        extracted = df[col].astype(str).str.lower().str.extract(UNIT_PATTERN)
        nums = pd.to_numeric(extracted[0], errors='coerce')
        units = extracted[1].str.strip()
        
        # Only process if 30%+ of non-null values match a valid measurement unit
        if nums.notna().sum() >= len(df) * 0.3:
            df[col] = nums
            if units.notna().any():
                df[f"{col}_unit"] = units

    return df


def clean_data(df:pd.DataFrame)->  pd.DataFrame:
    return (
        df.pipe(clean_columns)
          .pipe(normalize_text)
          .pipe(validation)               
          .pipe(drop_uninformative_columns)
          .pipe(convert_types)    
          .pipe(optimize)
    )
    
