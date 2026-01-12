# Import python packages
import pandas as pd
import streamlit as st
import requests
import urllib3
from snowflake.snowpark.functions import col

# Disable SSL warnings (API demo)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# -------------------------------
# App Header
# -------------------------------
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# -------------------------------
# User input
# -------------------------------
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)

# -------------------------------
# Snowflake connection (Streamlit Cloud compatible)
# -------------------------------
cnx = st.connection("snowflake")
session = cnx.session()

# -------------------------------
# Load fruit options (FRUIT_NAME + SEARCH_ON)
# -------------------------------
fruit_df = (
    session
    .table("smoothies.public.fruit_options")
    .select(col("FRUIT_NAME"), col("SEARCH_ON"))
)

fruit_rows = fruit_df.collect()

# Map display name -> search value
fruit_display_list = [row["FRUIT_NAME"] for row in fruit_rows]
fruit_search_map = {
    row["FRUIT_NAME"]: row["SEARCH_ON"]
    for row in fruit_rows
}

# -------------------------------
# Multiselect ingredients (UI uses FRUIT_NAME)
# -------------------------------
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_display_list,
    max_selections=5
)

# -------------------------------
# Insert order
# -------------------------------
if ingredients_list:
    ingredients_string = " ".join(ingredients_list)

    if st.button("Submit Order"):
        insert_stmt = (
            "insert into smoothies.public.orders (ingredients, name_on_order) "
            f"values ('{ingredients_string}', '{name_on_order}')"
        )

        session.sql(insert_stmt).collect()

        st.success(
            f"Your Smoothie is ordered, {name_on_order}!",
            icon="✅"
        )

# -------------------------------
# Nutrition information (API uses SEARCH_ON)
# -------------------------------
if ingredients_list:
    st.subheader("Nutrition Information")

    for fruit_chosen in ingredients_list:
        fruit_api_name = fruit_search_map.get(fruit_chosen)

        smoothiefroot_response = requests.get(
            f"https://www.smoothiefroot.com/api/fruit/{fruit_api_name}",
            verify=False,
            timeout=10
        )

        if smoothiefroot_response.status_code == 200:
            st.write(f"**{fruit_chosen}**")
            st.dataframe(
                smoothiefroot_response.json(),
                use_container_width=True
            )
        else:
            st.warning(
                f"Could not retrieve nutrition data for {fruit_chosen}"
            )
