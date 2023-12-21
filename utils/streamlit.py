import streamlit as st
def filter_selectboxes(filters: dict, columns=4):
    nb_columns = columns
    nb_rows = len(filters)//nb_columns+1
    for i in range(nb_rows):
        exec(f"cols{i} = st.columns(nb_columns)")

    #st.write(filter, filters[filter])
    for i, filter in enumerate(filters):
        row = str(i//nb_columns)
        column = str(i%nb_columns)
        col_ = f"cols{row}[{column}]"
        exec(f"""st.session_state["filter_{i}"] = {col_}.selectbox(label="{filter}", options=list((map(lambda x: x.strip(), filters["{filter}"]))), index=0)""")

    link = ""
    for i, (filter, values) in enumerate(filters.items()):
        #st.write(i, filter, values, st.session_state[f"filter_{i}"])
        data = filters[filter][st.session_state[f"filter_{i}"]]
        link += "" if len(data) == 0 else f"&{data}"