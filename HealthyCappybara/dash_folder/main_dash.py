'''
Code contributor:
Yijia (Gaga) He: 
    All related to dash exccept relationship_maps, radar graph implementation
    reading file, scatter_mapbox, Choropleth, Policy Implication graphs implementation,
    dash, app callbacks
Yue (Luan) Jian:
    All related to relationship_maps, radar graph implementation
    Choropleth; app callbacks 
Style and layout: Yijia (Gaga) He
Everything else: Yijia (Gaga) He
'''
import dash
from dash import Dash
from dash import dcc
from dash import html
import pandas as pd
import numpy as np
import os
import json
import pathlib
import matplotlib.colors as mcolors
from dash.dependencies import Input, Output
from plotly.graph_objs import *
from datetime import datetime as dt
import plotly.express as px
from .radar import *


demand = pathlib.Path(__file__).parent / "../cleaned_data/demand.csv"
health_score = pathlib.Path(__file__).parent / "../cleaned_data/health_score.csv"
doctors = pathlib.Path(__file__).parent / "../cleaned_data/doctors.csv"
us_zip = pathlib.Path(__file__).parent / "../cleaned_data/US_Zip"
boundary = pathlib.Path(__file__).parent / "../cleaned_data/Boundaries.geojson"
health_score_distribution = "./assets/health_score_distribution.jpg"
correlation_matrix_map = "./assets/correlation_matrix_map.jpg"
feature_importance = "./assets/feature_importance.jpg"
health_pic = "https://www.choa.org/-/media/Images/Childrens/global/heros/patients/during-your-stay/patient-girl-with-puzzle-in-pediatric-hospital-1440x748.jpg?h=748&la=en&w=1440&hash=8ABB2D5DFB87F45ABBA5F964A40165690E96E9BA"
cappy_gif = "https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExb2t6dDI5dmdqZzYycW80N2Nxb2htbHVlaGFreGFnMDV3bTFxOWVtZiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/FcVxYifmWOPKXL5x9F/giphy.gif"

# load data
raw_demand = pd.read_csv(demand, dtype=str)
raw_health_score = pd.read_csv(health_score, dtype=str)
raw_zip = pd.read_csv(us_zip, dtype=str)
raw_doctor = pd.read_csv(doctors)
demand_num = pd.read_csv(demand)
health_num = pd.read_csv(health_score)

# map all zipcodes with their lat & lon
def merge_all_dataframes(raw_demand, raw_health_score, raw_zip):
    merged_scores = pd.merge(raw_demand, raw_health_score, on="zcta_code", how="inner")
    merged_scores["Combined_Score"] = pd.to_numeric(
        merged_scores["Combined_Score"], errors="coerce"
    )
    merged_scores["combined_health_score"] = pd.to_numeric(
        merged_scores["combined_health_score"], errors="coerce"
    )
    merged_df = pd.merge(
        merged_scores, raw_zip, left_on="zcta_code", right_on="ZIP", how="left"
    )
    merged_df["LAT"] = pd.to_numeric(merged_df["LAT"], errors="coerce")
    merged_df["LNG"] = pd.to_numeric(merged_df["LNG"], errors="coerce")

    return merged_df


merged_df = merge_all_dataframes(raw_demand, raw_health_score, raw_zip)

with open(boundary, "r") as file:
    geojson = json.load(file)

# filter national geojson data to cook county
def filter_geojson_by_zipcode(geojson_data, target_zipcode):
    filtered_geojson = {"type": "FeatureCollection", "features": []}

    for feature in geojson_data["features"]:
        if feature["properties"].get("ZCTA5CE10") in target_zipcode:
            filtered_geojson["features"].append(feature)

    return filtered_geojson


cook_zipcodes = set(merged_df["zcta_code"])
filtered_gj = filter_geojson_by_zipcode(geojson, cook_zipcodes)

zip_lst = []

for i in merged_df["zcta_code"]:
    zip_lst.append(int(i))

health_threshold = merged_df["combined_health_score"].median()
demand_threshold = merged_df["Combined_Score"].median()
demand_column = [
    "demographic_demand",
    "vulnerability_demand",
    "poverty_demand",
    "development_demand",
]

health_column = [
    "quantity_score",
    "expenses_score",
    "quality_score",
]

# html style
colors = {
    "background": "#000000",
    "text": "#FFFFFF",
    "highlight": "#C0B0FC",
    "content_bg": "#FDFEFE",
    "grid": "grey",
    "mapbox_style": "open-street-map",
    "text_padding": "20px",
    "email_link": "#C0B0FC",
    "header_intro_bg": "#000000",
    "cluster": "#FFFFFF",
    "map_text": "#FFFFFF",
    "center": {"lat": 41.808611, "lon": -87.718889},
    "zoom": 8.5,
}
img_style = {
    "width": "100%",
    "height": "90%",
    "display": "flex",
    "justifyContent": "center",
}
dropdown_style = {"width": "50%", "margin": "0 auto"}
flex_style = {"display": "flex", "justifyContent": "center"}
text_style = {
    "marginLeft": "80px",
    "marginRight": "80px",
    "textAlign": "justify",
    "margin": "20px",
}
tab_style = {
    "border": "none",
    "backgroundColor": "#000000",
    "color": "#C0B0FC",
    "fontSize": "120%",
}
selected_tab_style = {
    "border": "none",
    "backgroundColor": "#9387C0",
    "color": "#000000",
    "fontWeight": "bold",
    "fontSize": "120%",
}
div_style_center = {"textAlign": "center"}
div_style_left_white = {
    "textAlign": "left",
    "color": colors["map_text"],
    "width": "100%",
    "padding": 5,
}
map_center = {"lat": 37.58394, "lon": -77.51376}

# dataset selection
initial_selection = "demand"
dropdown_options = [
    {"label": "Health Demand", "value": "demand"},
    {"label": "Health Accessibility Score", "value": "accessibility"},
]

# residential solutions
doctor_heat_map = px.scatter_mapbox(
    raw_doctor,
    lat="Y",
    lon="X",
    hover_name="name",
    color_discrete_sequence=["#9D7FBD"],
    zoom=3.5,
    height=500,
    center=map_center,
)

doctor_heat_map.update_layout(
    mapbox_style="white-bg",
    mapbox_layers=[
        {
            "below": "traces",
            "sourcetype": "raster",
            "sourceattribution": "Doctor Heat Map",
            "source": [
                "https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer/tile/{z}/{y}/{x}"
            ],
        }
    ],
    margin={"r": 0, "t": 0, "l": 0, "b": 0},
)

# relationship map plots
def assign_group(row, health_threshold, demand_threshold):
    health_status = (
        "High-Health"
        if row["combined_health_score"] >= health_threshold
        else "Low-Health"
    )
    demand_status = (
        "High-Demand" if row["Combined_Score"] >= demand_threshold else "Low-Demand"
    )
    return f"{health_status}, {demand_status}"


merged_df["Group"] = merged_df.apply(
    assign_group, axis=1, args=(health_threshold, demand_threshold)
)
tableau_colors = list(mcolors.TABLEAU_COLORS.values())
while len(tableau_colors) < len(merged_df["Group"].unique()):
    tableau_colors += tableau_colors
group_colors = {
    group: color for group, color in zip(merged_df["Group"].unique(), tableau_colors)
}

scatter_plot = px.scatter(
    merged_df,
    x="combined_health_score",
    y="Combined_Score",
    color="Group",
    hover_data=["zcta_code"],
    title="Community Clustering by Health and Demand Scores",
)
scatter_plot.update_layout(
    plot_bgcolor=colors["background"],
    paper_bgcolor=colors["background"],
    font=dict(color=colors["text"], family="Arial"),
)
scatter_plot.update_xaxes(showgrid=True, gridcolor=colors["grid"])
scatter_plot.update_yaxes(showgrid=True, gridcolor=colors["grid"])

map_cluster = px.choropleth_mapbox(
    merged_df,
    geojson=filtered_gj,
    locations="zcta_code",
    color="Group",
    featureidkey="properties.ZCTA5CE10",
    mapbox_style=colors["mapbox_style"],
    zoom=colors["zoom"],
    center=colors["center"],
    opacity=0.5,
    title="Distribution of Groups by Location",
)
map_cluster.update_layout(
    mapbox=dict(
        style=colors["mapbox_style"], center=colors["center"], zoom=colors["zoom"]
    ),
    margin={"r": 0, "t": 0, "l": 0, "b": 0},
    paper_bgcolor=colors["background"],
    font=dict(color=colors["text"], family="Arial"),
)

# App
app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}]
)

header_and_intro = html.Div(
    [
        html.Br(),
        html.Br(),
        html.H1("Healthy Cappybara", style={"textAlign": "center"}),
        html.P(
            "Welcome to the Healthy Cappybara World -- Let's explore the health accessibility in cook county!",
            style=text_style,
        ),
        html.Div(
            [
                html.Img(
                    src=health_pic,
                    style={"width": "100%", "height": "auto", "opacity": 0.5},
                )
            ],
            style={"display": "flex", "justifyContent": "center"},
        ),
        html.P(
            "For more detailed information, please visit other parts", style=text_style
        ),
    ],
    style={
        "position": "fixed",
        "zIndex": 0,
        "backgroundColor": colors["header_intro_bg"],
    },
)

team_members = [
    {"name": "Hourui Guo", "email": "hourui@uchicago.edu", "gif": cappy_gif},
    {"name": "Yijia He", "email": "yijiah@uchicago.edu", "gif": cappy_gif},
    {"name": "Yue Jian", "email": "jiany@uchicago.edu", "gif": cappy_gif},
    {"name": "Qi Zhao", "email": "zhaoq@uchicago.edu", "gif": cappy_gif},
]

team_member_divs = [
    html.Div(
        [
            html.P(f"{member['name']}: ", style=text_style),
            html.A(
                member["email"],
                href=f"mailto:{member['email']}",
                style={"color": colors["email_link"]},
            ),
            html.Br(),
            html.Img(src=member["gif"], style={"width": "100%", "height": "300px"}),
        ],
        style={
            "display": "inline-block",
            "width": "25%",
            "verticalAlign": "top",
            "textAlign": "center",
        },
    )
    for member in team_members
]

introduction_content = html.Div(
    [
        html.Br(),
        html.H2("Project Initiative", style=text_style),
        html.P(
            """
        Many individuals in the United States struggle to access necessary health care services.
        Healthy People 2030 defines Healthcare Accessibility as the capacity to obtain timely,
        high-quality, and affordable health care services. Aligning with the objective to enhance
        healthcare accessibility and promote healthier lives, our project aims to devise a
        systematic approach to improve access to healthcare within Cook County communities.
    """,
            style=text_style,
        ),
        html.Br(),
        html.Br(),
        html.H2("Team Member", style=text_style),
        html.Div(team_member_divs, style={"textAlign": "center"}),
    ],
    style={
        "position": "relative",
        "zIndex": 1000,
        "backgroundColor": colors["header_intro_bg"],
    },
)

accessibility_map = html.Div(
    [
        html.Br(),
        html.H2(
            "Accessibility Map", style={"textAlign": "center", "color": colors["text"]}
        ),
        html.Div(
            '''We've developed two models to assess health accessibility in Cook 
            County: Health Service Score and Population Demand Score, both 
            grounded in the Analytical Hierarchy Process (AHP) and Entropy 
            Weighting Method (EWM).''',
            style={"color": colors["text"], "padding": "5px"},
        ),
        html.Br(),
        html.Br(),
        html.Div(
            [
                html.Label(
                    "Please select the zipcode here:",
                    style={"textAlign": "center", "display": "block"},
                ),
                dcc.Dropdown(
                    id="zipcode-dropdown",
                    options=zip_lst,
                    value=60637,
                    style=dropdown_style,
                ),
            ],
            style=flex_style,
        ),
        html.Br(),
        html.H2(
            "Health and Demand Radar Charts",
            style={"textAlign": "center", "marginBottom": "20px"},
        ),
        html.Div(
            [
                dcc.Graph(
                    id="health-radar-graph",
                    style={"width": "48%", "display": "inline-block"},
                ),
                dcc.Graph(
                    id="demand-radar-graph",
                    style={"width": "48%", "display": "inline-block"},
                ),
            ],
            style={
                "display": "flex",
                "flexWrap": "wrap",
                "justifyContent": "space-between",
            },
        ),
        html.Br(),
        html.Div("Switch the dataset", style=text_style),
        dcc.Dropdown(
            id="dropdown",
            options=dropdown_options,
            value=initial_selection,
            style={"marginLeft": "20px", "width": "1350px", "height": "50px"},
        ),
        html.Br(),
        dcc.Graph(id="map"),
    ],
    style={
        "backgroundColor": colors["background"],
        "padding": "20px",
        "position": "relative",
        "zIndex": 1000,
    },
    className="five columns",
)

relationship_map = html.Div(
    [
        html.Br(),
        html.H2(
            "Relationship Analysis",
            style={"textAlign": "center", "color": colors["text"]},
        ),
        html.Div(
            "Please edit...",
            style={"textAlign": "left", "color": colors["text"], "padding": "30px"},
        ),
        html.Br(),
        html.Div(html.Img(src=health_score_distribution, style=img_style)),
        html.Br(),
        html.Div(html.Img(src=correlation_matrix_map, style=img_style)),
        html.Br(),
        html.Div(html.Img(src=feature_importance, style=img_style)),
        html.Br(),
    ],
    style={
        "backgroundColor": colors["background"],
        "position": "relative",
        "flexDirection": "column",
        "zIndex": 1000,
        "justifyContent": "center",
        "height": "100%",
        "display": "flex",
        "alignItems": "center",
    },
)

policy_implication = html.Div(
    [
        html.Br(),
        html.H2(
            "Community Clustering by Health and Demand Scores", style=div_style_center
        ),
        html.H3(id="some-id", style={"textAlign": "left", "color": colors["cluster"]}),
        dcc.Graph(
            id="scatter-plot-graph", figure=scatter_plot, style={"width": "100%"}
        ),
        html.Br(),
        html.H2("Distribution of Groups by Location", style=div_style_center),
        dcc.Graph(id="map_group", figure=map_cluster, style={"width": "100%"}),
        html.Br(),
    ],
    style={
        "position": "relative",
        "zIndex": 1000,
        "backgroundColor": colors["background"],
    },
)

residential_solution = html.Div(
    [
        html.Br(),
        html.H2("MAP 5", style=div_style_center),
        html.Div("Please edit", style=div_style_left_white),
        html.Div("Please edit", style=div_style_left_white),
        dcc.Graph(id="doctor_heat", figure=doctor_heat_map, style={"width": "100%"}),
        html.Br(),
        html.Br(),
    ],
    style={
        "position": "relative",
        "zIndex": 1000,
        "backgroundColor": colors["background"],
    },
)

app.layout = html.Div(
    [
        header_and_intro,
        html.Div(style={"height": "710px", "position": "sticky", "zIndex": "998"}),
        dcc.Tabs(
            id="tabs",
            value="tab-0",
            children=[
                dcc.Tab(
                    label="Introduction",
                    value="tab-0",
                    style=tab_style,
                    selected_style=selected_tab_style,
                ),
                dcc.Tab(
                    label="Accessibility Map",
                    value="tab-1",
                    style=tab_style,
                    selected_style=selected_tab_style,
                ),
                dcc.Tab(
                    label="Relationship Analysis",
                    value="tab-2",
                    style=tab_style,
                    selected_style=selected_tab_style,
                ),
                dcc.Tab(
                    label="Policy Implication",
                    value="tab-3",
                    style=tab_style,
                    selected_style=selected_tab_style,
                ),
                dcc.Tab(
                    label="Residential Solution",
                    value="tab-4",
                    style=tab_style,
                    selected_style=selected_tab_style,
                ),
            ],
            style={"position": "relative", "zIndex": "999", "border": "none"},
        ),
        html.Div(id="tabs-content"),
    ],
    style={
        "backgroundColor": colors["background"],
        "color": colors["text"],
        "marginTop": "-25px",
        "marginRight": "-10px",
        "marginLeft": "-10px",
        "marginBottom": "-20px",
        "fontFamily": "Times New Roman, Times, serif",
    },
)


@app.callback(Output("tabs-content", "children"), [Input("tabs", "value")])
def render_content(tab):
    if tab == "tab-0":
        return introduction_content
    elif tab == "tab-1":
        return accessibility_map
    elif tab == "tab-2":
        return relationship_map
    elif tab == "tab-3":
        return policy_implication
    elif tab == "tab-4":
        return residential_solution


@app.callback(Output("map", "figure"), [Input("dropdown", "value")])
def update_map(selected_option):
    color = "Combined_Score" if selected_option == "demand" else "combined_health_score"
    title = (
        "Demand Score by Location"
        if selected_option == "demand"
        else "Health Score by Location"
    )
    color_scale = "Reds" if selected_option == "demand" else "Blues"

    fig = px.choropleth_mapbox(
        merged_df,
        geojson=filtered_gj,
        locations="zcta_code",
        color=color,
        featureidkey="properties.ZCTA5CE10",
        mapbox_style="open-street-map",
        zoom=8.5,
        center={"lat": 41.808611, "lon": -87.718889},
        opacity=0.5,
        color_continuous_scale=color_scale,
        title=title,
    )

    fig.update_layout(
        height=800,
        paper_bgcolor="black",
        plot_bgcolor="black",
        font=dict(color="white", family="Times New Roman, Times, serif"),
    )

    if selected_option != "demand":
        fig.update_layout(coloraxis_colorbar=dict(title="Average Health Score"))

    return fig


@app.callback(
    [Output("demand-radar-graph", "figure"), Output("health-radar-graph", "figure")],
    [Input("zipcode-dropdown", "value")],
)
def update_radar_charts(zip_code):
    demand_fig = plot_demand_radar_chart(demand_num, zip_code, demand_column)
    health_fig = plot_health_radar_chart(health_num, zip_code, health_column)
    return demand_fig, health_fig


@app.callback(Output("scatter-plot-graph", "figure"), [Input("some-input", "value")])
def update_scatter_plot(_):
    fig = px.scatter(
        merged_df,
        x="Combined_Score",
        y="combined_health_score",
        labels={
            "Combined_Score": "Demand Score",
            "combined_health_score": "Health Score",
        },
        title="Demand vs Health Score by Zip Code",
    )
    return fig
