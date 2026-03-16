from smd_obs import obs_analysis, save_results
from database import db_conn 

df = obs_analysis( 1.1, 1.1, -8, db_conn)

if df is not None:
    print(df.tail()) 

    last_smd_wd = df.iloc[-1]['smd_wd']
    last_smd_md = df.iloc[-1]['smd_md']
    last_smd_pd = df.iloc[-1]['smd_pd']
    
    print(f"Well({last_smd_wd}), Mod({last_smd_md}), Poor({last_smd_pd})")

    if df is not None:
        save_results(df, db_conn)