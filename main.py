import streamlit as st
import sqlite3
import pandas as pd
from html_css import *

st.set_page_config(initial_sidebar_state="collapsed", page_title='P961', layout="centered", page_icon='lebanon.png')
st.markdown(hide_streamlit_items, unsafe_allow_html=True)

db_file_path = "plates.db"


# Function to connect to the SQLite database
def connect_to_db(file_path):
    try:
        conn = sqlite3.connect(file_path)
        return conn
    except Exception as e:
        st.error(f"Failed to connect to the database. Error: {e}")
        return None


# Function to fetch unique code values from the database
def get_unique_codes(conn):
    query = "SELECT DISTINCT CodeDesc FROM CARMDI"
    try:
        df = pd.read_sql(query, conn)
        unique_codes = df["CodeDesc"].dropna().tolist()
        unique_codes.sort()
        return unique_codes
    except Exception as e:
        st.error(f"Failed to fetch unique code values. Error: {e}")
        return []


# Function to search the database using the provided parameters
def search_db(conn, actual_nb, code):
    query = "SELECT * FROM CARMDI WHERE 1=1"
    params = []

    # For plate number, use exact matching if provided
    if actual_nb:
        query += " AND ActualNB = ?"
        params.append(actual_nb)
    else:
        query += " AND ActualNB LIKE ?"
        params.append("%")

    # For the code, if a specific code is selected, use an exact match.
    if code:
        query += " AND CodeDesc = ?"
        params.append(code)

    try:
        df = pd.read_sql(query, conn, params=params)
        return df
    except Exception as e:
        st.error(f"Failed to execute query. Error: {e}")
        return pd.DataFrame()  # Return an empty DataFrame in case of error


# Streamlit app
def main():
    st.title("Plate961")

    # Connect to the SQLite database
    conn = connect_to_db(db_file_path)
    if conn is None:
        return

    # Create two columns: 0.3 for Code and 0.7 for Plate Number
    col1, col2 = st.columns([0.3, 0.7])

    with col1:
        # Dropdown menu for Code with an empty option as default
        unique_codes = get_unique_codes(conn)
        selected_code = st.selectbox("Code", options=[""] + unique_codes)

    with col2:
        # Input field for Plate Number
        actual_nb = st.text_input("Plate Number")

    # Search button
    if st.button("Search"):
        if not actual_nb:
            st.warning("Please enter a Plate Number to search.")
        else:
            df = search_db(conn, actual_nb, selected_code)
            if not df.empty:
                if len(df) > 1:
                    st.info("Multiple results found. Please click below to expand the search results.")
                    with st.expander("Show Search Results"):
                        st.dataframe(df)
                else:
                    row = df.iloc[0]
                    col_left, col_right = st.columns(2)
                    left_markdown = f"""
**Full Name:** {row['Prenom']} {row['Nom']}  
**Phone Number:** {row['TelProp']}  
**Birth Details:** {row['AgeProp']} / {row['BirthPlace']}  
**Mother Name:** {row['NomMere']}  
**Address:** {row['Addresse']}
                    """
                    right_markdown = f"""
**Car Description:** {row['MarqueDesc']} {row['TypeDesc']}  
**Model Year:** {row['PRODDATE']}  
**Chassis#:** {row['Chassis']}  
**Engine#:** {row['Moteur']}
                    """
                    with col_left:
                        st.markdown(left_markdown)
                    with col_right:
                        st.markdown(right_markdown)
            else:
                st.error("No results found.")

    # Close the connectio
    conn.close()


if __name__ == "__main__":
    main()
