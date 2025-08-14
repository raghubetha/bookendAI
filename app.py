from dash import Dash, page_registry, page_container, dcc
import dash_bootstrap_components as dbc


# --- app Instantiation ---
app = Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.FLATLY, dbc.icons.FONT_AWESOME])
server = app.server

# --- Define the desired order ---
page_order = ['About', 'Explorer', 'Your Profile','Book Deep Dive', 'Books']

# Sort the page registry based on your defined order
sorted_pages = sorted(page_registry.values(), key=lambda page: page_order.index(page['name']))

# --- Navigation Bar ---
navbar = dbc.NavbarSimple(
    children=[
        #Create a link for each page registered in the pages folder
        dbc.NavItem(dbc.NavLink(page['name'], href=page['relative_path'], active='exact'))
        for page in sorted_pages
        if page.get('nav', True)  # Only include pages where 'nav' is not False

    ],
    brand="Bookend AI",
    brand_href="/",
    color="primary",
    dark=True,
    className="mb-4"

)

#--- Main Layout ---
app.layout = dbc.Container([
    navbar,
    #the content of each page will be rendered in this container
    page_container,
    dcc.Store(id='shared-filter-store')
], fluid=True)

# --- Run the app ---

#app.layout = html.Div(children=[html.H1("Average vs Number of Ratings"), html.Br(), dcc.Graph(id= 'rating-scatterplot',figure=fig)])

if __name__ == '__main__':
    app.run(debug=True)

