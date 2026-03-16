import pandas as pd
import math
from sqlalchemy import text
from database import db_conn
from analysis import calculate_pe_from_obs, calculated_smd

def obs_analysis(init_wd, init_md, init_pd, db_conn):
# initial smd = 2026-02-28
    current_smd_wd = init_wd # well draiend
    current_smd_md = init_md # moderately drained
    current_smd_pd = init_pd # poorly drained

    query = text("""
             select date, maxtp, mintp, wdsp, glorad, rain
             from obs_hist where date between '2026-03-01' and '2026-03-14'
             order by date
                 """)
    
    try:
        with db_conn.connect() as conn:
            obs_df = pd.read_sql(query, conn)
        
        if obs_df.empty:
            print("No Data Found")
            return None

        results = []

        for _, row in obs_df.iterrows():
            obs_row = {
                'max_temp': row['maxtp'],
                'min_temp': row['mintp'],
                'wdsp': row['wdsp'],
                'glorad': row['glorad'],
                'rain': row['rain']
            }
        
            pe = calculate_pe_from_obs(obs_row)
        
            _, current_smd_wd, _ = calculated_smd(current_smd_wd, pe, row['rain'], 'well')
            _, current_smd_md, _ = calculated_smd(current_smd_md, pe, row['rain'], 'moderately')
            _, current_smd_pd, _ = calculated_smd(current_smd_pd, pe, row['rain'], 'poorly')

            results.append({
                'date': row['date'],
                'pe': pe,
                'rain': row['rain'],
                'smd_wd': current_smd_wd,
                'smd_md': current_smd_md,
                'smd_pd': current_smd_pd
            })

        final_df = pd.DataFrame(results)
        return final_df

    except Exception as e:
        print(f"error: {e}")
        return None

def save_results(df, conn):
    if df is None or df.empty:
        print("No Data Found")
        return

    query = text("""
        update obs_hist set
            pe = :pe,
            smd_wd = :smd_wd,
            smd_md = :smd_md,
            smd_pd = :smd_pd
            where date = :date
            """)

    try:
        with db_conn.begin() as conn: 
            for _, row in df.iterrows():
                conn.execute(query, {
                    'pe': row['pe'],
                    'smd_wd': row['smd_wd'],
                    'smd_md': row['smd_md'],
                    'smd_pd': row['smd_pd'],
                    'date': row['date']
                })
        print(f"✅ {len(df)} succeed")
    except Exception as e:
        print(f"error: {e}")

    

    
    