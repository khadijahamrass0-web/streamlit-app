import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Dashboard Data Visualization",
    layout="wide"
)

st.title("📊 Dashboard Data Visualization")

uploaded_file = st.file_uploader(
    "Importer un fichier CSV ou Excel",
    type=["csv", "xlsx"]
)

if uploaded_file is not None:

    # Chargement du fichier
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    # Limitation 100 lignes et 20 colonnes
    if len(df) > 100:
        st.warning("Le fichier contient plus de 100 lignes.")
    if len(df.columns) > 20:
        st.warning("Le fichier contient plus de 20 colonnes.")

    st.subheader("Aperçu des données")
    st.dataframe(df)

    # Détection automatique des dates
    for col in df.columns:
        try:
            df[col] = pd.to_datetime(df[col])
        except:
            pass

    # Détermination du type des variables
    variable_types = {}

    for col in df.columns:

        if pd.api.types.is_datetime64_any_dtype(df[col]):
            variable_types[col] = "Date"

        elif pd.api.types.is_numeric_dtype(df[col]):
            variable_types[col] = "Quantitative"

        else:
            variable_types[col] = "Qualitative"

    st.sidebar.header("Options")

    # Choix variables
    x_var = st.sidebar.selectbox(
        "Variable X",
        df.columns
    )

    y_options = ["Aucune"] + list(df.columns)

    y_var = st.sidebar.selectbox(
        "Variable Y",
        y_options
    )

    graph_type = st.sidebar.selectbox(
        "Type de graphique",
        [
            "Automatique",
            "Histogramme",
            "Bar Chart",
            "Scatter Plot",
            "Boxplot",
            "Line Chart"
        ]
    )

    # Filtre simple
    filter_column = st.sidebar.selectbox(
        "Filtrer par",
        ["Aucun"] + list(df.columns)
    )

    filtered_df = df.copy()

    if filter_column != "Aucun":

        if variable_types[filter_column] == "Qualitative":

            selected_values = st.sidebar.multiselect(
                "Valeurs",
                filtered_df[filter_column].dropna().unique()
            )

            if selected_values:
                filtered_df = filtered_df[
                    filtered_df[filter_column].isin(selected_values)
                ]

    # Détermination automatique du graphique
    if graph_type == "Automatique":

        if y_var == "Aucune":

            if variable_types[x_var] == "Qualitative":
                graph_type = "Bar Chart"

            elif variable_types[x_var] == "Quantitative":
                graph_type = "Histogramme"

            else:
                graph_type = "Line Chart"

        else:

            x_type = variable_types[x_var]
            y_type = variable_types[y_var]

            if x_type == "Quantitative" and y_type == "Quantitative":
                graph_type = "Scatter Plot"

            elif (
                (x_type == "Qualitative" and y_type == "Quantitative")
                or
                (x_type == "Quantitative" and y_type == "Qualitative")
            ):
                graph_type = "Boxplot"

            elif (
                x_type == "Date"
                or
                y_type == "Date"
            ):
                graph_type = "Line Chart"

            else:
                graph_type = "Bar Chart"

    # Titre dynamique
    if y_var == "Aucune":
        st.subheader(f"{graph_type} : {x_var}")
    else:
        st.subheader(f"{graph_type} : {x_var} vs {y_var}")

    fig = None

    try:

        # Histogramme
        if graph_type == "Histogramme":

            fig = px.histogram(
                filtered_df,
                x=x_var
            )

        # Bar Chart
        elif graph_type == "Bar Chart":

            counts = (
                filtered_df[x_var]
                .value_counts()
                .reset_index()
            )

            counts.columns = [x_var, "Count"]

            fig = px.bar(
                counts,
                x=x_var,
                y="Count"
            )

        # Scatter Plot
        elif graph_type == "Scatter Plot":

            if y_var != "Aucune":

                fig = px.scatter(
                    filtered_df,
                    x=x_var,
                    y=y_var
                )

        # Boxplot
        elif graph_type == "Boxplot":

            if y_var != "Aucune":

                if variable_types[x_var] == "Qualitative":

                    fig = px.box(
                        filtered_df,
                        x=x_var,
                        y=y_var
                    )

                else:

                    fig = px.box(
                        filtered_df,
                        x=y_var,
                        y=x_var
                    )

        # Line Chart
        elif graph_type == "Line Chart":

            if y_var == "Aucune":

                temp = (
                    filtered_df[x_var]
                    .value_counts()
                    .sort_index()
                    .reset_index()
                )

                temp.columns = [x_var, "Count"]

                fig = px.line(
                    temp,
                    x=x_var,
                    y="Count"
                )

            else:

                fig = px.line(
                    filtered_df,
                    x=x_var,
                    y=y_var
                )

        if fig is not None:
            st.plotly_chart(
                fig,
                use_container_width=True
            )

    except Exception as e:
        st.error(f"Erreur : {e}")

    # Informations sur les variables
    st.subheader("Types des variables")

    info_df = pd.DataFrame({
        "Variable": list(variable_types.keys()),
        "Type": list(variable_types.values())
    })

    st.dataframe(info_df)
