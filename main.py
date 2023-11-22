import osmnx as ox
import folium
import networkx as nx
import random
from geopy.geocoders import Nominatim
from IPython.display import display

def find_routes(start_point, end_point, graph):
    start_node = ox.distance.nearest_nodes(graph, start_point[1], start_point[0])
    end_node = ox.distance.nearest_nodes(graph, end_point[1], end_point[0])
    shortest_route = nx.shortest_path(graph, start_node, end_node, weight='length')
    fastest_route = nx.shortest_path(graph, start_node, end_node, weight='travel_time')
    return shortest_route, fastest_route

def plot_point_and_circle_on_map(map_obj, latitude, longitude, radius_meters=500):
    folium.Circle(location=[latitude, longitude], radius=radius_meters, color='blue', fill=True, 
                  fill_color='blue', fill_opacity=0.1).add_to(map_obj)

def assign_random_pollution_values(graph, seed=42):
    random.seed(seed)
    for node in graph.nodes:
        if 'pollution_level' not in graph.nodes[node]:
            graph.nodes[node]['pollution_level'] = random.randint(20, 100)

def calculate_average_pollution(route, graph):
    pollution_values = [graph.nodes[node].get('pollution_level', 0) for node in route]
    return sum(pollution_values) / len(pollution_values) if pollution_values else None

def plot_route_on_folium(map_obj, route, graph, color):
    for u, v in zip(route[:-1], route[1:]):
        lat_lng1 = (graph.nodes[u]['y'], graph.nodes[u]['x'])
        lat_lng2 = (graph.nodes[v]['y'], graph.nodes[v]['x'])
        folium.PolyLine([lat_lng1, lat_lng2], color=color, weight=5).add_to(map_obj)

def add_legend(map_obj):
    legend_html = """
    <div style="position: fixed; bottom: 50px; left: 20px; width: 220px; height: 120px; 
    border:2px solid grey; z-index:9999; font-size:14px; background-color:white;">
      <p><strong>Legend</strong></p>
      <p style="color:green;">&lt; 30: Low Pollution</p>
      <p style="color:blue;">30 - 60: Moderate Pollution</p>
      <p style="color:red;">&gt; 60: High Pollution</p>
    </div>
    """
    map_obj.get_root().html.add_child(folium.Element(legend_html))

def add_information_box(map_obj, avg_pollution_shortest, avg_pollution_fastest):
    lower_pollution_route = "Shortest" if avg_pollution_shortest < avg_pollution_fastest else "Fastest"
    info_html = f"""
    <div style="position: fixed; 
                 top: 50px; left: 50px; width: 300px; height: 180px; 
                 border:2px solid grey; z-index:9999; font-size:14px;
                 background-color:white; padding: 10px;">
      <h4>Route Information</h4>
      <p>Average Pollution (Shortest Route): {avg_pollution_shortest:.2f}</p>
      <p>Average Pollution (Fastest Route): {avg_pollution_fastest:.2f}</p>
      <p>Recommended Route: {lower_pollution_route} (Lower Pollution)</p>
    </div>
    """
    map_obj.get_root().html.add_child(folium.Element(info_html))

# Function to search for location using Geopy
def search_location(query):
    geolocator = Nominatim(user_agent="search_box_app")
    location = geolocator.geocode(query, exactly_one=True)

    if location:
        print(f"Location found: {location.address}")
        print(f"Latitude: {location.latitude}, Longitude: {location.longitude}")
        return location.latitude, location.longitude
    else:
        print("Location not found. Please try again with a different query.")
        return None

if __name__== "main":
    # Get starting location
    while True:
        start_input = input("Enter starting location or 'exit' to quit: ")
        
        if start_input.lower() == 'exit':
            exit()

        start_location = search_location(start_input)
        if start_location:
            break

    # Get ending location
    while True:
        end_input = input("Enter ending location or 'exit' to quit: ")
        
        if end_input.lower() == 'exit':
            exit()

        end_location = search_location(end_input)
        if end_location:
            break

    # Load the street map data
    G = ox.graph_from_point(start_location, dist=3000, network_type='drive')

    # Assign random pollution values to each node in the graph
    assign_random_pollution_values(G)

    # Find routes
    shortest, fastest = find_routes(start_location, end_location, G)

    # Calculate average pollution levels along the routes
    average_pollution_shortest = calculate_average_pollution(shortest, G)
    average_pollution_fastest = calculate_average_pollution(fastest, G)

    # Create a Folium map
    m = folium.Map(location=start_location, zoom_start=14)

    # Plot the routes
    plot_route_on_folium(m, shortest, G, 'blue')
    plot_route_on_folium(m, fastest, G, 'red')

    # Plot circles on the map
    for location in [start_location, end_location]:
        plot_point_and_circle_on_map(m, location[0], location[1])

    # Display the legend and information box
    add_legend(m)
    add_information_box(m, average_pollution_shortest, average_pollution_fastest)

    # Display the map using the display function
    display(m)
    