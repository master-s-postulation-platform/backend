import matplotlib.pyplot as plt
import base64
from io import BytesIO
from fbprophet import Prophet

def get_graph():
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    graph = base64.b64encode(image_png)
    graph = graph.decode('utf-8')
    buffer.close()
    return graph

def get_plot_pie(x,y):
    plt.switch_backend('AGG')
    plt.figure(figsize=(7,4))
    plt.title('Postulants by Gender')
    plt.pie(y, labels= x, autopct='%1.1f%%')
    plt.xticks(rotation=45)
    plt.xlabel('')
    plt.tight_layout()
    graph = get_graph()
    return graph

def get_plot_histogram(x):
    plt.switch_backend('AGG')
    plt.figure(figsize=(6,4))
    plt.title('Postulants Age')
    plt.hist(x, bins = 10)
    plt.xlabel('Ages')
    plt.ylabel('Counts')
    graph = get_graph()
    return graph

def get_plot_bar(x,y):
    plt.switch_backend('AGG')
    plt.figure(figsize=(6,4))
    plt.title('Postulants Civil Status')
    plt.bar(x,y)
    plt.xlabel('Status')
    plt.ylabel('Counts')
    graph = get_graph()
    return graph

def get_forecast(data):
    m = Prophet(daily_seasonality = True) # the Prophet class (model)
    m.fit(data) # fit the model using all data
    future = m.make_future_dataframe(periods=365) #we need to specify the number of days in future
    prediction = m.predict(future)
    m.plot(prediction)
    plt.title("Prediction of number of postulants")
    plt.xlabel("Date")
    plt.ylabel("Number of postulants")
    graph = get_graph()
    return graph

def get_components(data):
    m = Prophet(daily_seasonality = True) # the Prophet class (model)
    m.fit(data) # fit the model using all data
    future = m.make_future_dataframe(periods=365) #we need to specify the number of days in future
    prediction = m.predict(future)
    m.plot_components(prediction)
    graph = get_graph()
    return graph