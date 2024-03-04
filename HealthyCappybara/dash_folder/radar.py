import pandas as pd
import numpy as np
import plotly.graph_objs as go
from plotly.offline import iplot



def plot_demand_radar_chart(df, zip_code, demand_columns):

    zip_data = df[df['zcta_code'] == zip_code]
    # If no data found for the zip_code, return an empty figure

    if zip_data.empty:
        print("No data found for the specified ZIP code.")
        return go.Figure()
    
    # Extract the values for the demand columns and round to two decimals
    values = [round(num, 2) for num in zip_data[demand_columns].values.flatten()]
    values += values[:1]  # Repeat the first value at the end to close the radar chart
    
    # Number of variables we're plotting
    num_vars = len(demand_columns)
    
    # Compute angle each bar is centered on
    angles = [n / float(num_vars) * 360 for n in range(num_vars)]
    angles += angles[:1]  # Complete the loop
    
    # Custom circular dotted lines for grid
    max_val = max(values)
    radial_ticks = np.linspace(0, max_val + max_val * 0.35, num=6)  # Adjust the number of radial ticks here
    custom_angular_gridlines = []
    for radial_tick in radial_ticks:
        theta = np.linspace(0, 360, 360)  # Full circle divided into 360 degrees
        r = [radial_tick] * 360
        custom_angular_gridlines.append(go.Scatterpolar(
            r=r,
            theta=theta,
            mode='lines',
            line=dict(color='rgba(255,255,255,0.5)', width=1, dash='dot'),
            showlegend=False,
            hoverinfo='none'
        ))
    
    # Initialise the radar plot layout
    layout = go.Layout(
        title={
            'text': 'Demand Score for ' + str(zip_code),
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': dict(color='rgba(255,255,255,1)')
        },
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, max_val + max_val * 0.1],
                tickvals=radial_ticks[1:],  # Skip the center tick for aesthetics
                tickcolor='rgba(255,255,255,0.5)',
                color='rgba(255,255,255,0.5)',
                gridcolor='rgba(255,255,255,0)',  # Set gridcolor to transparent
            ),
            angularaxis=dict(
                tickvals=angles[:-1],
                ticktext=demand_columns,
                color='rgba(255,255,255,1)',
                gridcolor='rgba(255,255,255,0)',  # Set angular gridcolor to transparent
            ),
            bgcolor='rgba(0,0,0,0)'  # Transparent background inside the polar area
        ),
        paper_bgcolor='rgba(0,0,0,0)',  # Transparent background
        plot_bgcolor='rgba(0,0,0,0)',  # Transparent background
        showlegend=True
    )
    
    # Plot data
    trace = go.Scatterpolar(
        r=values,
        theta=angles,
        fill='toself',
        name=f'Demand Combined Score: {round(zip_data["Combined_Score"].iloc[0], 2)}',
        line=dict(color='rgba(106,168,79,1)'),
        marker=dict(color='rgba(106,168,79,1)', size=10, line=dict(color='rgba(106,168,79,1)', width=2)),
        hovertemplate='Score: %{r}<extra></extra>'
    )
    
    # Add the data and the custom angular gridlines to the figure
    fig = go.Figure(data=[trace] + custom_angular_gridlines, layout=layout)

    # Return the figure object instead of displaying it
    return fig



def plot_health_radar_chart(df, zip_code, demand_columns):
    # Filter the DataFrame for the given zip_code
    zip_data = df[df['zcta_code'] == zip_code]
    
    # If no data found for the zip_code, return an empty figure with a message
    if zip_data.empty:
        print("No data found for the specified ZIP code.")
        return go.Figure(layout=dict(title=dict(text='No data found for the specified ZIP code.')))
    
    # Extract the values for the demand columns and round to two decimals
    values = [round(num, 2) for num in zip_data[demand_columns].values.flatten()]
    values += values[:1]  # Repeat the first value at the end to close the radar chart
    
    # Number of variables we're plotting
    num_vars = len(demand_columns)
    
    # Compute angle each bar is centered on
    angles = [n / float(num_vars) * 360 for n in range(num_vars)]
    angles += angles[:1]  # Complete the loop
    
    # Custom circular dotted lines for grid
    max_val = max(values)
    radial_ticks = np.linspace(0, max_val + max_val * 0.35, num=6)  # Adjust the number of radial ticks here
    custom_angular_gridlines = []
    for radial_tick in radial_ticks:
        theta = np.linspace(0, 360, 360)  # Full circle divided into 360 degrees
        r = [radial_tick] * 360
        custom_angular_gridlines.append(go.Scatterpolar(
            r=r,
            theta=theta,
            mode='lines',
            line=dict(color='rgba(255,255,255,0.5)', width=1, dash='dot'),
            showlegend=False,
            hoverinfo='none'
        ))
    
    # Initialise the radar plot layout
    layout = go.Layout(
        title={
            'text': 'Health Score for ' + str(zip_code),
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': dict(color='rgba(255,255,255,1)')
        },
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, max_val + max_val * 0.1],
                tickvals=radial_ticks[1:],
                tickcolor='rgba(255,255,255,0.5)',  # Skip the center tick for aesthetics
                color='rgba(255,255,255,0.5)',
                gridcolor='rgba(255,255,255,0)',  
            ),
            angularaxis=dict(
                tickvals=angles[:-1],
                ticktext=demand_columns,
                color='rgba(255,255,255,1)',
                gridcolor='rgba(255,255,255,0)',  # Set angular gridcolor to transparent
            ),
            bgcolor='rgba(0,0,0,0)'  # Transparent background inside the polar area
        ),
        paper_bgcolor='rgba(0,0,0,0)',  # Transparent background
        plot_bgcolor='rgba(0,0,0,0)',  # Transparent background
        showlegend=True
    )
    
    # Plot data
    trace = go.Scatterpolar(
        r=values,
        theta=angles,
        fill='toself',
        name=f'Health Combined Score: {round(zip_data["combined_health_score"].iloc[0], 2)}',
        line=dict(color='rgba(255,0,0,1)'),  # Red color for the radar line
        marker=dict(color='rgba(255,0,0,1)', size=10, line=dict(color='rgba(255,0,0,1)', width=2)),
        hovertemplate='Score: %{r}<extra></extra>'
    )
    
    
    # Add the data and the custom angular gridlines to the figure
    fig = go.Figure(data=[trace] + custom_angular_gridlines, layout=layout)

    # Return the figure object instead of displaying it
    return fig
