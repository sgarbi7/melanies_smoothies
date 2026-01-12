# Import python packages
import streamlit as st
import requests
from snowflake.snowpark.functions import col

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)

# Snowflake connection (Streamlit Cloud compatible)
cnx = st.connection("snowflake")
session = cnx.session()

my_dataframe = (
    session
    .table("smoothies.public.fruit_options")
    .select(col("FRUIT_NAME"))
)

ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    my_dataframe.collect(),  # <- IMPORTANTE
    max_selections=5
)

if ingredients_list:
    ingredients_string = ""

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen["FRUIT_NAME"] + " "

    my_insert_stmt = (
        "insert into smoothies.public.orders (ingredients, name_on_order) "
        "values ('" + ingredients_string + "', '" + name_on_order + "')"
    )

    if st.button("Submit Order"):
        session.sql(my_insert_stmt).collect()
        st.success(
            f"Your Smoothie is ordered, {name_on_order}!",
            icon="✅"
        )

# Nutrition information
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
