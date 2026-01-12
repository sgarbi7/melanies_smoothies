# Import python packages
import streamlit as st
import requests
from snowflake.snowpark.functions import col

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

# Load fruit options
fruit_df = (
    session
    .table("smoothies.public.fruit_options")
    .select(col("FRUIT_NAME"))
)

fruit_list = [row["FRUIT_NAME"] for row in fruit_df.collect()]

# -------------------------------
# Multiselect ingredients
# -------------------------------
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_list,
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
# Nutrition information
# -------------------------------
st.subheader("Nutrition Information")

smoothiefruit_response = requests.get(
    "https://my.smoothiefruit.com/api/fruit/watermelon"
)

if smoothiefruit_response.status_code == 200:
    st.dataframe(
        smoothiefruit_response.json(),
        use_container_width=True
    )
else:
    st.error("Could not retrieve nutrition data.")
