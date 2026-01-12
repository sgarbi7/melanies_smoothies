# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)

# Conexão com Snowflake
cnx = st.connection("snowflake")
session = cnx.session()

my_dataframe = (
    session
    .table("smoothies.public.fruit_options")
    .select(col("FRUIT_NAME"))
)

ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    my_dataframe,
    max_selections=5
)

if ingredients_list:
    ingredients_string = ""

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + " "

    # Criação do comando SQL
    my_insert_stmt = (
        "insert into smoothies.public.orders (ingredients, name_on_order) "
        "values ('" + ingredients_string + "', '" + name_on_order + "')"
    )

    time_to_insert = st.button("Submit Order")

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success(
            f"Your Smoothie is ordered, {name_on_order}!",
            icon="✅"
        )

# Nova seção para exibir informações nutricionais
st.subheader("Nutrition Information")

smoothiefruit_response = requests.get(
    "https://my.smoothiefruit.com/api/fruit/watermelon"
)

# Exibe o JSON da API de forma organizada em um dataframe
if smoothiefruit_response.status_code == 200:
    st.dataframe(
        data=smoothiefruit_response.json(),
        use_container_width=True
    )
else:
    st.error("Could not retrieve nutrition data.")
