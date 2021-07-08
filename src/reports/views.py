from django.shortcuts import render

from .utils import get_plot_pie, get_plot_histogram, get_plot_bar, get_forecast, get_components
from functools import reduce

from profiles.models import Profile, User, JobStatus,CivilStatus, Gender
import pandas as pd

import geopandas as gpd
import geopy
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import matplotlib.pyplot as plt
import folium
from folium.plugins import FastMarkerCluster


from datetime import date


def main_view(request):
    # Querysets
    qs = Profile.objects.all().values()
    qs2 = User.objects.all().values() 
    qs3 = JobStatus.objects.all().values()
    qs4 = CivilStatus.objects.all().values()
    qs5 = Gender.objects.all().values()

    df_qs = pd.DataFrame(qs)
    df_qs2 = pd.DataFrame(qs2)
    df_qs3 = pd.DataFrame(qs3)
    df_qs4 = pd.DataFrame(qs4)
    df_qs5 = pd.DataFrame(qs5)
    

    data_frames = [df_qs, df_qs2, df_qs3, df_qs4, df_qs5 ]

    df_merge = reduce(lambda  left,right: pd.merge(left,right,on=['id'],how='outer'), data_frames)


    calc_age =  date.today().year - pd.DatetimeIndex(df_merge['birthday']).year
    df_merge['age'] = calc_age


    #Data Frame Top Score 
    sel_col = df_merge[['first_name','last_name' ,'gender','age','has_job', 'company_name', 'change_opt', 'salary', 'total_score', 'c_status']].sort_values('total_score', ascending=False)
    sel_col.reset_index(drop=True, inplace=True)

    age = qs.values('birthday')

    
    #Pie Data and Plot
    counts_s = dict(df_qs5['gender'].value_counts())
    x = list(counts_s.keys())
    y = list(counts_s.values())
    chart = get_plot_pie(x,y)

    #Histogram
    age = df_merge['age']
    histogram = get_plot_histogram(age)

    #Salary describe
    a = df_merge['salary'].max()

    # Single
    count_civil = dict(df_merge['c_status'].value_counts())
    c_status = list(count_civil.keys())
    c_values = list(count_civil.values())
    civil = get_plot_bar(c_status,c_values)

    #Time series
    time_count = pd.DatetimeIndex(df_merge.created_y).strftime('%Y-%m-%d')
    time_count = pd.DataFrame(time_count)
    time_count = dict(time_count['created_y'].value_counts())

    date_create = list(time_count.keys())
    counts_create = list(time_count.values())
    data = pd.DataFrame(list(zip(date_create,counts_create)), columns=['ds','y']) 
    forecast = get_forecast(data)
    components = get_components(data)


    locator = Nominatim(user_agent="myGeocoder")
    location = locator.geocode("Champ de Mars, Paris, France")
    print("Latitude = {}, Longitude = {}".format(location.latitude, location.longitude))





    context = {
        'df': sel_col.to_html,
        'chart': chart,
        'histo': histogram,
        'civil': civil,
        'forecast': forecast,
        'components': components,
    }

    return render(request, 'reports/main.html', context)
