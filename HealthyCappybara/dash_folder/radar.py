import pandas as pd
import numpy as np
import plotly.graph_objs as go
from plotly.offline import iplot

COLOR_DICT = {'demand' : 'rgba(106,168,79,1)',
              'health' : 'rgba(255,0,0,1)'}

def plot_radar_chart(df, zip_code, score_columns, score_type):
    # Validate score_type
    valid_score_types = ['demand', 'health']
    if score_type not in valid_score_types:
        raise ValueError(f"score_type must be one of {valid_score_types}")

    # Filter the DataFrame for the given zip_code
    zip_data = df[df['zcta_code'] == zip_code]
    
    # If no data found for the zip_code, return an empty figure with a message
    if zip_data.empty:
        print(f"No data found for the specified ZIP code: {zip_code}")
        return go.Figure(layout=dict(title=dict(text=f'No data found for the specified ZIP code: {zip_code}')))
    
    # Extract the values for the score columns and round to two decimals
    values = [round(num, 2) for num in zip_data[score_columns].values.flatten()]
    values += values[:1]  # Repeat the first value at the end to close the radar chart
    
    # Number of variables we're plotting
    num_vars = len(score_columns)
    
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
            line=dict(color=COLOR_DICT[score_type], width=1, dash='dot'),
            showlegend=False,
            hoverinfo='none'
        ))
    
    # Initialise the radar plot layout
    title_text = f'{score_type.capitalize()} Score for {zip_code}'
    layout = go.Layout(
        title={
            'text': title_text,
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': dict(color=COLOR_DICT[score_type])
        },
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, max_val + max_val * 0.1],
                tickvals=radial_ticks[1:],  # Skip the center tick for aesthetics
                tickcolor=COLOR_DICT[score_type],
                color=COLOR_DICT[score_type],
                gridcolor=COLOR_DICT[score_type],  # Set gridcolor to transparent
            ),
            angularaxis=dict(
                tickvals=angles[:-1],
                ticktext=score_columns,
                color=COLOR_DICT[score_type],
                gridcolor=COLOR_DICT[score_type],  # Set angular gridcolor to transparent
            ),
            bgcolor='rgba(0,0,0,0)'  # Transparent background inside the polar area
        ),
        paper_bgcolor='rgba(0,0,0,0)',  # Transparent background
        plot_bgcolor='rgba(0,0,0,0)',  # Transparent background
        showlegend=True
    )
    
    # Determine the trace name based on score type
    if score_type == 'demand':
        trace_name = f'{score_type.capitalize()} Combined Score: {round(zip_data["Combined_Score"].iloc[0], 2)}'
    else:
        trace_name = f'{score_type.capitalize()} Combined Score: {round(zip_data["combined_health_score"].iloc[0], 2)}'
    
    # Plot data
    trace = go.Scatterpolar(
        r=values,
        theta=angles,
        fill='toself',
        name=trace_name,
        line=dict(color=COLOR_DICT[score_type]),
        marker=dict(color=COLOR_DICT[score_type], size=10, line=dict(color=COLOR_DICT[score_type], width=2)),
        hovertemplate='Score: %{r}<extra></extra>'
    )
    
    # Add the data and the custom angular gridlines to the figure
    fig = go.Figure(data=[trace] + custom_angular_gridlines, layout=layout)

    return fig