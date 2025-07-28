# import pandas as pd
# import yfinance as yf
# from datetime import datetime, timedelta
# import os

# def analyze_stock_recommendations(input_file_path, output_file_path):
#     """
#     Reads stock recommendations, appends the analysis to a master Excel file,
#     and avoids creating duplicates.
#     """
#     try:
#         new_df = pd.read_excel(input_file_path)
#     except FileNotFoundError:
#         print(f"❌ Error: The file '{input_file_path}' was not found.")
#         return
#     except Exception as e:
#         print(f"❌ An error occurred while reading '{input_file_path}': {e}")
#         return

#     if os.path.exists(output_file_path):
#         print(f"📖 Reading existing data from '{output_file_path}'...")
#         existing_df = pd.read_excel(output_file_path)
#     else:
#         print(f"✨ Creating new master file: '{output_file_path}'")
#         existing_df = pd.DataFrame()

#     results = []
#     print("🚀 Starting analysis on new data...")

#     for index, row in new_df.iterrows():
#         row.index = row.index.str.strip()
        
#         stock_name = row['stock_name']
#         recommendation_date = pd.to_datetime(row['date'])
#         recommendation_type = row['recommendation_type']
        
#         # Handle target price ranges (e.g., "450-455")
#         target_price = float(str(row['target_price']).split('-')[0])
#         stop_loss = float(row['stop_loss'])
#         holding_period = row.get('holding_period', None)

#         period_str = str(holding_period).lower().strip()
#         if pd.isna(holding_period) or period_str == '' or 'not mentioned' in period_str:
#             holding_days = 42
#         elif 'week' in period_str:
#             holding_days = int(''.join(filter(str.isdigit, period_str))) * 7
#         else:
#             holding_days = int(''.join(filter(str.isdigit, period_str)))
            
#         start_date = recommendation_date
#         end_date = start_date + timedelta(days=holding_days + 5) # Add buffer

#         try:
#             ticker = f"{stock_name}.NS"
#             stock_data = yf.download(ticker, start=start_date, end=end_date, progress=False, auto_adjust=True)
#             if stock_data.empty:
#                 stock_data = yf.download(stock_name, start=start_date, end=end_date, progress=False, auto_adjust=True)
            
#             # Defensive check: Remove duplicate dates if any
#             stock_data = stock_data[~stock_data.index.duplicated(keep='first')]

#             if stock_data.empty:
#                 print(f"⚠️ Warning: No data found for {stock_name}. Skipping.")
#                 continue
#         except Exception as e:
#             print(f"⚠️ Warning: Could not download data for {stock_name}. Skipping. Error: {e}")
#             continue

#         # --- BUG FIX #1: Handle "Not Mentioned" in current_price ---
#         current_price_raw = row['current_price']
#         if isinstance(current_price_raw, str) and 'not mentioned' in current_price_raw.lower():
#             # Use the opening price on the first day of data we found
#             current_price = stock_data.iloc[0]['Open']
#         else:
#             current_price = float(current_price_raw)
#         # --- End of Fix ---

#         target_hit, stop_loss_hit, final_price_used = "No", "No", None

#         # Loop through the valid holding period
#         analysis_period = stock_data[stock_data.index <= start_date + timedelta(days=holding_days)]
#         for _, daily_data in analysis_period.iterrows():
#             # --- BUG FIX #2: Ensure single boolean value for comparison ---
#             if (daily_data['High'] >= target_price).any():
#                 if recommendation_type == 'Buy':
#                     target_hit, final_price_used = "Yes", target_price
#                     break
#             if (daily_data['Low'] <= stop_loss).any():
#                 if recommendation_type == 'Buy':
#                     stop_loss_hit, final_price_used = "Yes", stop_loss
#                     break
            
#             if (daily_data['Low'] <= target_price).any():
#                  if recommendation_type == 'Sell':
#                     target_hit, final_price_used = "Yes", target_price
#                     break
#             if (daily_data['High'] >= stop_loss).any():
#                 if recommendation_type == 'Sell':
#                     stop_loss_hit, final_price_used = "Yes", stop_loss
#                     break
#         # --- End of Fix ---
        
#         if final_price_used is None and not analysis_period.empty:
#             final_price_used = analysis_period.iloc[-1]['Close']
#         elif final_price_used is None:
#             final_price_used = current_price

#         actual_profit_loss = (final_price_used - current_price) if recommendation_type == 'Buy' else (current_price - final_price_used)

#         def get_price_after_days(days):
#             if len(stock_data) > days:
#                 return stock_data.iloc[days]['Close']
#             return 0.00 

#         # Store the original row's data and add the new analysis columns
#         output_row = row.to_dict()
#         output_row.update({
#             'current_price': current_price, # Update with fetched price if needed
#             'target_hit': target_hit, 'stop_loss_hit': stop_loss_hit,
#             'actual_profit_loss': actual_profit_loss,
#             'price_after_2_weeks': get_price_after_days(10),
#             'price_after_4_weeks': get_price_after_days(20),
#             'price_after_6_weeks': get_price_after_days(30),
#             'final_price_used': final_price_used
#         })
#         results.append(output_row)

#     if not results:
#         print("✅ No new valid recommendations to add. Master file is already up to date.")
#         return

#     new_results_df = pd.DataFrame(results)
#     combined_df = pd.concat([existing_df, new_results_df], ignore_index=True)

#     unique_cols = ['date', 'analyst_name', 'stock_name', 'recommendation_type', 'target_price', 'stop_loss']
#     combined_df.drop_duplicates(subset=unique_cols, keep='last', inplace=True)
    
#     analyst_accuracy = combined_df.groupby('analyst_name')['target_hit'].apply(lambda x: (x == 'Yes').sum() / len(x) * 100 if len(x) > 0 else 0)
#     combined_df['accuracy_score'] = combined_df['analyst_name'].map(analyst_accuracy).round(2)
#     combined_df['total_profit'] = combined_df['actual_profit_loss'].sum()
    
#     combined_df.to_excel(output_file_path, index=False, float_format="%.2f")
#     print(f"✅ Success! Analysis complete. All data saved to '{output_file_path}'")

# if __name__ == "__main__":
#     master_output_file = "master_stock_analysis.xlsx"
#     input_file = input("Enter the name of the Excel file to analyze (e.g., 'my_stocks.xlsx'): ")
#     analyze_stock_recommendations(input_file, master_output_file)



# import pandas as pd
# import yfinance as yf
# from datetime import datetime, timedelta
# import os

# def get_correct_ticker(stock_name):
#     """
#     Cleans the stock name and maps common names to their correct yfinance ticker.
#     This function makes the script more robust against variations in stock names.
#     """
#     # Dictionary for special cases where the name doesn't easily map to the ticker
#     TICKER_MAP = {
#         "GODREJ AGROVET": "GODREJAGRO.NS",
#         "BEL": "BEL.NS",
#         "LODHA": "LODHA.NS",
#         "TEJAS NETWORKS": "TEJASNET.NS",
#         "D B REALTY": "DBREALTY.NS",
#         "TIME TECHNO PLASTICS": "TIMETECHNO.NS",
#         "ION EXCHANGE": "IONEXCHANG.NS",
#         "APTECH": "APTECHT.NS", # Aptech has a 'T' in its ticker
#         "PRADEEP PHOSPHATES": "PARADEEP.NS" # The ticker is 'PARADEEP'
#     }
    
#     clean_name = stock_name.strip().upper()
    
#     # Return from the map if the name is a known special case
#     if clean_name in TICKER_MAP:
#         return TICKER_MAP[clean_name]
#     else:
#         # Standard ticker construction for other cases
#         return f"{clean_name.replace(' ', '')}.NS"

# def analyze_stock_recommendations(input_file_path, output_file_path):
#     """
#     Safely reads new stock recommendations, processes them robustly by skipping bad rows,
#     and appends ONLY the new ones to a master analysis file without data loss.
#     """
#     try:
#         new_df = pd.read_excel(input_file_path)
#         print(f"✅ Successfully read new data from '{input_file_path}'.")
#     except Exception as e:
#         print(f"❌ An error occurred while reading the input file: {e}"); return

#     # Define unique columns and standardize date format for reliable comparison
#     unique_cols = ['date', 'analyst_name', 'stock_name', 'recommendation_type']
#     new_df['date'] = pd.to_datetime(new_df['date']).dt.strftime('%Y-%m-%d')

#     if os.path.exists(output_file_path):
#         print(f"📖 Reading existing data from '{output_file_path}'...")
#         existing_df = pd.read_excel(output_file_path)
#         existing_df['date'] = pd.to_datetime(existing_df['date']).dt.strftime('%Y-%m-%d')
        
#         # This logic ensures we only process rows that are not already in the master file
#         new_df['merge_key'] = new_df[unique_cols].astype(str).agg('-'.join, axis=1)
#         existing_df['merge_key'] = existing_df[unique_cols].astype(str).agg('-'.join, axis=1)
#         rows_to_process = new_df[~new_df['merge_key'].isin(existing_df['merge_key'])].copy()
#         existing_df.drop(columns=['merge_key'], inplace=True, errors='ignore')
#         rows_to_process.drop(columns=['merge_key'], inplace=True, errors='ignore')
#     else:
#         print(f"✨ Master file not found. Creating a new one.")
#         existing_df = pd.DataFrame()
#         rows_to_process = new_df.copy()

#     if rows_to_process.empty:
#         print("✅ No new recommendations found to analyze. Your master file is already up to date."); return

#     print(f"🚀 Found {len(rows_to_process)} new recommendations to analyze...")
#     newly_analyzed_results = []

#     for index, row in rows_to_process.iterrows():
#         stock_name = row.get('stock_name', 'Unknown')
#         # --- Master Try-Except Block to handle ANY error in a row ---
#         try:
#             # --- Robust Data Conversion ---
#             recommendation_date = pd.to_datetime(row['date'])
#             recommendation_type = row['recommendation_type']
#             target_price = float(str(row['target_price']).split('-')[0].strip())
#             stop_loss = float(row['stop_loss'])
            
#             period_str = str(row.get('holding_period', '')).lower().strip()
#             if 'not mentioned' in period_str or not period_str: holding_days = 42
#             else: holding_days = int("".join(filter(str.isdigit, period_str))) * 7 if 'week' in period_str else int("".join(filter(str.isdigit, period_str)))
            
#             start_date, end_date = recommendation_date, recommendation_date + timedelta(days=holding_days + 10)
            
#             # --- Ticker Handling ---
#             ticker = get_correct_ticker(stock_name)
#             stock_data = yf.download(ticker, start=start_date, end=end_date, progress=False, auto_adjust=True)
#             if stock_data.empty: print(f"⚠️ Warning: No data found for {stock_name} ({ticker}). Skipping."); continue

#             # --- Price Handling ---
#             current_price_raw = row['current_price']
#             if isinstance(current_price_raw, str) and 'not mentioned' in current_price_raw.lower():
#                 current_price = float(stock_data.iloc[0]['Open'])
#             else:
#                 current_price = float(current_price_raw)

#             # --- Analysis Logic ---
#             target_hit, stop_loss_hit, final_price_used = "No", "No", current_price
#             analysis_period = stock_data[stock_data.index <= start_date + timedelta(days=holding_days)]
            
#             for _, daily_data in analysis_period.iterrows():
#                 # Correctly compare single float values to prevent ambiguity errors
#                 high, low = float(daily_data['High']), float(daily_data['Low'])
#                 if recommendation_type == 'Buy':
#                     if high >= target_price: target_hit, final_price_used = "Yes", target_price; break
#                     if low <= stop_loss: stop_loss_hit, final_price_used = "Yes", stop_loss; break
#                 else: # Sell
#                     if low <= target_price: target_hit, final_price_used = "Yes", target_price; break
#                     if high >= stop_loss: stop_loss_hit, final_price_used = "Yes", stop_loss; break

#             if target_hit == "No" and stop_loss_hit == "No" and not analysis_period.empty:
#                 final_price_used = float(analysis_period.iloc[-1]['Close'])
            
#             actual_profit_loss = (final_price_used - current_price) if recommendation_type == 'Buy' else (current_price - final_price_used)
            
#             def get_price_after_days(days): return float(stock_data.iloc[days]['Close']) if len(stock_data) > days else 0.00
            
#             output_row = row.to_dict()
#             output_row.update({
#                 'current_price': current_price, 'target_hit': target_hit, 'stop_loss_hit': stop_loss_hit,
#                 'actual_profit_loss': actual_profit_loss, 'price_after_2_weeks': get_price_after_days(10),
#                 'price_after_4_weeks': get_price_after_days(20), 'price_after_6_weeks': get_price_after_days(30),
#                 'final_price_used': final_price_used })
#             newly_analyzed_results.append(output_row)
        
#         except Exception as e:
#             print(f"🚨 Error processing row {index} ({stock_name}): '{e}'. Skipping.")
#             continue

#     if not newly_analyzed_results:
#         print("✅ Analysis finished, but no new valid rows could be processed."); return

#     # --- Final Combination and Calculation ---
#     newly_analyzed_df = pd.DataFrame(newly_analyzed_results)
#     combined_df = pd.concat([existing_df, newly_analyzed_df], ignore_index=True)
    
#     # Drop old calculation columns to ensure they are always fresh
#     for col in ['accuracy_score', 'total_profit']:
#         if col in combined_df.columns: combined_df.drop(columns=[col], inplace=True)

#     combined_df['actual_profit_loss'] = pd.to_numeric(combined_df['actual_profit_loss'], errors='coerce').fillna(0)
    
#     analyst_accuracy = combined_df.groupby('analyst_name')['target_hit'].apply(lambda x: (x == 'Yes').sum() * 100 / len(x) if len(x) > 0 else 0)
#     combined_df['accuracy_score'] = combined_df['analyst_name'].map(analyst_accuracy)
    
#     combined_df['total_profit'] = combined_df['actual_profit_loss'].sum()
    
#     combined_df['date'] = pd.to_datetime(combined_df['date']).dt.date
    
#     combined_df.to_excel(output_file_path, index=False, float_format="%.2f")
#     print(f"✅ Success! Analysis complete. Master file '{output_file_path}' is fully updated.")

# if __name__ == "__main__":
#     master_output_file = "master_stock_analysis.xlsx"
#     input_file = input("Enter the name of the Excel file to analyze: ")
#     analyze_stock_recommendations(input_file, master_output_file)


import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import os

def get_correct_ticker(stock_name):
    """
    Cleans the stock name and maps common names to their correct yfinance ticker.
    This makes the script more robust against variations in stock names.
    """
    TICKER_MAP = {
        "GODREJ AGROVET": "GODREJAGRO.NS", "BEL": "BEL.NS", "LODHA": "LODHA.NS",
        "TEJAS NETWORKS": "TEJASNET.NS", "D B REALTY": "DBREALTY.NS",
        "TIME TECHNO PLASTICS": "TIMETECHNO.NS", "ION EXCHANGE": "IONEXCHANG.NS",
        "APTECH": "APTECHT.NS", "PRADEEP PHOSPHATES": "PARADEEP.NS"
    }
    clean_name = stock_name.strip().upper()
    return TICKER_MAP.get(clean_name, f"{clean_name.replace(' ', '')}.NS")

def calculate_average_price(price_input):
    """
    Calculates the average price from a string that might be a single number
    or a range like '795-796'.
    """
    try:
        price_str = str(price_input).strip()
        if '-' in price_str:
            parts = [float(p.strip()) for p in price_str.split('-')]
            return sum(parts) / len(parts)
        else:
            return float(price_str)
    except (ValueError, TypeError):
        raise ValueError(f"Invalid price format: {price_input}")

def analyze_stock_recommendations(input_file_path, output_file_path):
    """
    Safely reads new recommendations, robustly processes each row, and appends
    ONLY the new ones to a master file without data loss.
    """
    try:
        new_df = pd.read_excel(input_file_path)
        print(f"✅ Successfully read new data from '{input_file_path}'.")
    except Exception as e:
        print(f"❌ An error occurred while reading the input file: {e}"); return

    unique_cols = ['date', 'analyst_name', 'stock_name', 'recommendation_type']
    new_df['date'] = pd.to_datetime(new_df['date']).dt.strftime('%Y-%m-%d')

    if os.path.exists(output_file_path):
        print(f"📖 Reading existing data from '{output_file_path}'...")
        existing_df = pd.read_excel(output_file_path)
        existing_df['date'] = pd.to_datetime(existing_df['date']).dt.strftime('%Y-%m-%d')
        
        new_df['merge_key'] = new_df[unique_cols].astype(str).agg('-'.join, axis=1)
        existing_df['merge_key'] = existing_df[unique_cols].astype(str).agg('-'.join, axis=1)
        rows_to_process = new_df[~new_df['merge_key'].isin(existing_df['merge_key'])].copy()
        existing_df.drop(columns=['merge_key'], inplace=True, errors='ignore')
        rows_to_process.drop(columns=['merge_key'], inplace=True, errors='ignore')
    else:
        print(f"✨ Master file not found. Creating a new one.")
        existing_df = pd.DataFrame()
        rows_to_process = new_df.copy()

    if rows_to_process.empty:
        print("✅ No new recommendations found to analyze."); return

    print(f"🚀 Found {len(rows_to_process)} new recommendations to analyze...")
    newly_analyzed_results = []

    for index, row in rows_to_process.iterrows():
        stock_name = row.get('stock_name', 'Unknown')
        try:
            recommendation_date = pd.to_datetime(row['date'])
            recommendation_type = row['recommendation_type']
            target_price = calculate_average_price(row['target_price'])
            stop_loss = calculate_average_price(row['stop_loss'])
            
            period_str = str(row.get('holding_period', '')).lower().strip()
            digits = "".join(filter(str.isdigit, period_str))
            if not digits:
                holding_days = 42
            else:
                holding_days = int(digits) * 7 if 'week' in period_str else int(digits)

            start_date, end_date = recommendation_date, recommendation_date + timedelta(days=holding_days + 10)
            
            ticker = get_correct_ticker(stock_name)
            stock_data = yf.download(ticker, start=start_date, end=end_date, progress=False, auto_adjust=True)
            if stock_data.empty: print(f"⚠️ Warning: No data for {stock_name} ({ticker}). Skipping."); continue

            current_price_raw = row['current_price']
            if isinstance(current_price_raw, str) and 'not mentioned' in current_price_raw.lower():
                current_price = float(stock_data.iloc[0]['Open'])
            else:
                current_price = calculate_average_price(current_price_raw)

            target_hit, stop_loss_hit, final_price_used = "No", "No", current_price
            analysis_period = stock_data[stock_data.index <= start_date + timedelta(days=holding_days)]
            
            for _, daily_data in analysis_period.iterrows():
                high, low = float(daily_data['High']), float(daily_data['Low'])
                if recommendation_type == 'Buy':
                    if high >= target_price: target_hit, final_price_used = "Yes", target_price; break
                    if low <= stop_loss: stop_loss_hit, final_price_used = "Yes", stop_loss; break
                else:
                    if low <= target_price: target_hit, final_price_used = "Yes", target_price; break
                    if high >= stop_loss: stop_loss_hit, final_price_used = "Yes", stop_loss; break

            if target_hit == "No" and stop_loss_hit == "No" and not analysis_period.empty:
                final_price_used = float(analysis_period.iloc[-1]['Close'])
            
            actual_profit_loss = (final_price_used - current_price) if recommendation_type == 'Buy' else (current_price - final_price_used)
            
            def get_price_after_days(days): return float(stock_data.iloc[days]['Close']) if len(stock_data) > days else 0.00
            
            output_row = row.to_dict()
            output_row.update({
                'current_price': current_price, 'target_price': target_price, 'stop_loss': stop_loss,
                'target_hit': target_hit, 'stop_loss_hit': stop_loss_hit,
                'actual_profit_loss': actual_profit_loss, 'price_after_2_weeks': get_price_after_days(10),
                'price_after_4_weeks': get_price_after_days(20), 'price_after_6_weeks': get_price_after_days(30),
                'final_price_used': final_price_used })
            newly_analyzed_results.append(output_row)
        
        except Exception as e:
            print(f"🚨 Error processing row {index} ({stock_name}): '{e}'. This row will be skipped.")
            continue

    if not newly_analyzed_results:
        print("✅ Analysis finished, but no new valid rows could be processed."); return

    newly_analyzed_df = pd.DataFrame(newly_analyzed_results)
    combined_df = pd.concat([existing_df, newly_analyzed_df], ignore_index=True)
    
    # Drop accuracy_score to ensure it's always recalculated
    if 'accuracy_score' in combined_df.columns:
        combined_df.drop(columns=['accuracy_score'], inplace=True)

    combined_df['actual_profit_loss'] = pd.to_numeric(combined_df['actual_profit_loss'], errors='coerce').fillna(0)
    
    # Recalculate analyst accuracy for the entire file
    analyst_accuracy = combined_df.groupby('analyst_name')['target_hit'].apply(lambda x: (x == 'Yes').sum() * 100 / len(x) if len(x) > 0 else 0)
    combined_df['accuracy_score'] = combined_df['analyst_name'].map(analyst_accuracy).round(2)
    
    # The 'total_profit' calculation has been removed.
    
    combined_df['date'] = pd.to_datetime(combined_df['date']).dt.date
    
    combined_df.to_excel(output_file_path, index=False, float_format="%.2f")
    print(f"✅ Success! Analysis complete. Master file '{output_file_path}' is fully updated.")

if __name__ == "__main__":
    master_output_file = "master_stock_analysis.xlsx"
    input_file = input("Enter the name of the Excel file to analyze: ")
    analyze_stock_recommendations(input_file, master_output_file)