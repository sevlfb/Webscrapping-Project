import streamlit as st
import pandas as pd

df = pd.read_csv("indeed_jobs.csv")
df = df.fillna(" ")
st.dataframe(df)