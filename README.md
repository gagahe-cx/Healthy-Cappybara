# Healthcare Accessibility Scores in Cook County

Many individuals in the United States struggle to access necessary health care services. [Healthy People 2030](https://health.gov/healthypeople/objectives-and-data/browse-objectives/health-care-access-and-quality) defines Healthcare Accessibility as the capacity to obtain timely, high-quality, and affordable health care services. Aligning with the objective to enhance healthcare accessibility and promote healthier lives, our project aims to devise a systematic approach to improve access to healthcare within Cook County communities.

Healthcare Accessibility can be broken down into three key components:
* Healthcare Service Capacity: This refers to the availability of healthcare services, indicated by the number, costs, and quality ratings of hospitals, nursing homes, and home care agencies.
* Population Demand: This encompasses the demographic need for healthcare services, factoring in population size, growth, poverty levels, and vulnerability.
* Geographic Impedance: This assesses how easily residents can reach healthcare providers' locations, reflected by the gap between healthcare service capacity and population demand.

Our project employs a combination of weighting, machine learning, and geographical methods to create an index and predictive model for healthcare accessibility. We integrate data from various sources, primarily obtained through web scraping and searches, including information from the Centers for [Medicare & Medicaid Services](https://www.cms.gov/data-research), [US Census Bureau](https://data.census.gov/), and [Healthgrades](https://www.healthgrades.com/), which collectively provide details on over three million U.S. healthcare providers.

Our project offers three distinct applications beneficial to both policymakers and residents:
* Data Visualization: It enables the visualization of healthcare accessibility across various attributes, offering a clear view of the current landscape.
* Analysis and Prediction: This feature calculates a healthcare accessibility score for each community, identifying crucial factors influencing access to healthcare.
* Solutions Platform/Roadmap: An interactive dashboard allows policymakers to identify communities with significant healthcare gaps, while enabling residents to locate timely, high-quality healthcare providers based on their location.

### Team Member (Last Name in Alphabetic Order)
Hourui Guo, Yijia He, Yue Jian, Qi Zhao

## Package used
pandas\
geopandas\
folium\
plotly\
dash\
json\
numpy\
base64\
还有其他的加上

## Data Sources
### Health Service Part
(1) Physicians' information on healthgrades\
Source: [healthgrades website](https://www.healthgrades.com/)\
Collection Way: Web-scraping\
Responsible team members: Yijia & Yue

(2) Patient survey (HCAHPS) - In Patient Hospital\
Source: [Data.CMS website](https://data.cms.gov/provider-data/dataset/dgck-syfz)\
Collection Way: CSV file available\
Responsible team members: Hourui

(3) Outpatient and Ambulatory Surgery CAHPS Survey\
Source: [Data.CMS website](https://data.cms.gov/provider-data/dataset/48nr-hqxx)\
Collection Way: CSV file available\
Responsible team members: Hourui

(4) Home Health Care - Patient Survey(HHCAHPS)\
Source: [Data.CMS website](https://data.cms.gov/provider-data/dataset/ccn4-8vby)\
Collection Way: CSV file available\
Responsible team members: Hourui

(5) Nursing Home Provider Information\
Source: [Data.CMS website](https://data.cms.gov/provider-data/dataset/4pq5-n9py)\
Collection Way: CSV file available\
Responsible team members: Hourui

(6) Health Expenses&Beds for Hospital - Hospital Provider Cost Report
Source: [Data.CMS website](https://data.cms.gov/provider-compliance/cost-report/hospital-provider-cost-report)\
Collection Way: CSV file available
Responsible team members: Qi

(7) Health Expenses&Beds for Nursing - Skilled Nursing Facility Cost Report
Source: [Data.CMS website](https://data.cms.gov/provider-compliance/cost-report/skilled-nursing-facility-cost-report)\
Collection Way: CSV file available
Responsible team members: Qi

(8) Health Expenses for Homecare- Home Health Agency Cost Report
Source: [Data.CMS website](https://data.cms.gov/provider-compliance/cost-report/home-health-agency-cost-report)\
Collection Way: CSV file available
Responsible team members: Qi

### Population Demand Part
(1) Demographic data 
Source: [US Census Bureau](https://data.census.gov/table?q=demographic&g=050XX00US17031$8600000)
Collection Way: CSV file available
Responsible team members: Qi

(2) Income Data
Source: [US Census Bureau](https://data.census.gov/table?t=Earnings&g=050XX00US17031)
Collection Way: CSV file available
Responsible team members: Qi

(3) Health Insurance Coverage
Source: [US Census Bureau](https://data.census.gov/table?t=Health%20Insurance&g=050XX00US17031)
Collection Way: CSV file available
Responsible team members: Qi

(4) Employment
Source: [US Census Bureau](https://data.census.gov/table?t=Employment&g=050XX00US17031)
Collection Way: CSV file available
Responsible team members: Qi

(5) Social Characteristics
Source: [US Census Bureau](https://data.census.gov/table?q=Selected%20Characteristics&g=050XX00US17031$8600000)
Collection Way: Shapefile available
Responsible team members: Qi

(6) Poverty Situation
Source: [US Census Bureau](https://data.census.gov/table?q=poverty&g=050XX00US17031$8600000)
Collection Way: Shapefile available
Responsible team members: Qi

### Geographic information
(2) ZCTA Code Shapefile
Source: [US Census Bureau](https://www.census.gov/geographies/mapping-files/time-series/geo/cartographic-boundary.html)
Collection Way: Shapefile available
Responsible team members: Qi

(1) Zip Code with Longitude and Latitude
Source: [US Zip Codes from 2013 Government Data](https://gist.github.com/erichurst/7882666)\
Collection Way: GeoJson available
Responsible team members: Qi

# Instruction to launch the application


