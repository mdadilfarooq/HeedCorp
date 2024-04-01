import dash, hashlib, os
from dash import Input, Output, State, html
import dash_bootstrap_components as dbc
from pymongo import MongoClient

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SKETCHY], suppress_callback_exceptions=True)
server = app.server

app.title = 'Heed'

db = dbc.Row(
    dbc.Button(
            "Pilot",
            value="pilot",
            color="success",
            className="me-1",
            disabled=True,
            id="db",
        ),
    className="g-0 ms-auto flex-nowrap mt-3 mt-md-0",
    align="center",
)

header = dbc.Navbar(
    dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(html.Img(src='assets/logo.png', height="30px")),
                    dbc.Col(dbc.NavbarBrand(children=[
                                "Heed ",
                                html.Span("1.5", style={"color": "gray", "font-size": "0.8em"}),
                            ], className="ms-2")),
                ],
                align="center",
                className="g-0",
            ),
            dbc.NavbarToggler(id="navbar-toggler", n_clicks=0),
            dbc.Collapse(
                db,
                id="navbar-collapse",
                is_open=False,
                navbar=True,
            ),
        ]
    ),
    color="dark",
    dark=True,
    className="rounded"
)

form = html.Div(
    [
        html.Div(
            [
                dbc.RadioItems(
                    id="collection",
                    className="btn-group",
                    inputClassName="btn-check",
                    labelClassName="btn btn-outline-success",
                    labelCheckedClassName="active",
                    options=[
                        {"label": "Register", "value": "register"},
                        {"label": "Redeem", "value": "redeem"},
                    ],
                    value="register",
                ),
            ],
            className="d-grid gap-2 radio-group",
        ),
        dbc.FormFloating([
            dbc.Input(type="text", id="pubid", placeholder="", maxlength="8"),
            dbc.Label("Public key"),
        ], style={"marginTop": "10px"}),
        dbc.FormFloating([
            dbc.Input(type="text", id="pin", placeholder="", maxlength="4"),
            dbc.Label("Secret PIN"),
            dbc.FormText(id='instruction', color="secondary"),
        ], style={"marginTop": "10px"}),
        dbc.FormFloating([
            dbc.Input(type="text", id="name", placeholder="", maxlength="30"),
            dbc.Label("Name"),
        ], id='name-div', style={"display": "none"}),
        dbc.FormFloating([
            dbc.Input(type="text", id="email", placeholder="", maxlength="30"),
            dbc.Label("Email"),
        ], id='email-div', style={"marginTop": "10px", "display": "none"}),
        html.Hr(),
        dbc.Checkbox(
            id="checkbox",
            value=False,
        ),
        dbc.Button("Submit", color="success", disabled=True, id="submit-button", active=True, style={"width": "100%"}),
    ],
    className="container", style={'width': '50%','marginTop': '20px', "border": "2px solid black", "padding": "10px", "border-radius": "10px"}
)

app.layout = html.Div([
    header,
    form,
    dbc.Toast(id="alert", is_open=False, duration=4000, style={"position": "fixed", "top": 66, "right": 10, "width": 350}),
    html.Div("MADE WITH ❤️ BY HEEDCORP™️", style={'textAlign': 'center', 'marginTop': '20px', 'marginBottom': '20px','fontSize': '10px', 'color': 'gray'}),
    ], className='container', style={'marginTop': '10px'})

@app.callback(
    Output("pubid", "invalid"), Output("pin", "invalid"), Output("name", "invalid"), Output("email", "invalid"),
    [Input("pubid", "value"), Input("pin", "value"), Input("name", "value"), Input("email", "value")],
    prevent_initial_call=True,
)
def validate_input(pubid, pin, name, email):
    pubid_invalidity = (False if len(pubid) == 8 and pubid.isalnum() else True) if pubid else None
    pin_invalidity = (False if len(pin) == 4 and pin.isnumeric() else True) if pin else None
    name_invalidity = False if name else None
    email_invalidity = False if email else None

    return pubid_invalidity, pin_invalidity, name_invalidity, email_invalidity

@app.callback(
    Output("submit-button", "disabled", allow_duplicate=True),
    [Input("pubid", "invalid"), Input("pin", "invalid"), Input("name", "invalid"), Input("email", "invalid"), Input("checkbox", "value")],
    [State("submit-button", "active"), State("collection", "value")],
    prevent_initial_call=True,
)
def enable_submit(pubid, pin, name, email, checkbox, active, collection):
    if active:
        if collection == "register":
            return False if all([True if pubid == False else False, True if pin == False else False, checkbox]) else True
        elif collection == "redeem":
            return False if all([True if pubid == False else False, True if pin == False else False, True if name == False else False, True if email == False else False, checkbox]) else True
    return True

@app.callback(
    Output("submit-button", "active", allow_duplicate=True),
    Output("submit-button", "children", allow_duplicate=True),
    Output("submit-button", "disabled", allow_duplicate=True),
    [Input("submit-button", "n_clicks")],
    prevent_initial_call=True,
)
def loader(n_clicks):
    if n_clicks:
        return False, [dbc.Spinner(size="sm"), " Working..."], True
    
@app.callback(
    Output("submit-button", "children", allow_duplicate=True),
    Output("submit-button", "active", allow_duplicate=True),
    Output("pubid", "value", allow_duplicate=True),
    Output("pin", "value", allow_duplicate=True),
    Output("name", "value", allow_duplicate=True),
    Output("email", "value", allow_duplicate=True),
    Output("checkbox", "value", allow_duplicate=True),
    Output("alert", "is_open"),
    Output("alert", "children"),
    Output("alert", "icon"),
    Output("alert", "header"),
    [Input("submit-button", "active")],
    [State("collection", "value"), State("pubid", "value"), State("pin", "value"), State("name", "value"), State("email", "value"), State("db", "value")],
    prevent_initial_call=True,
    allow_duplicate=True
)
def upload(active, collection, pubid, pin, name, email, db):
    connection = os.getenv('connection')
    if not active:
        try:
            with MongoClient(connection) as client:
                db = client.get_database(db)
                register = db.register
                redeem = db.redeem
                details = db.details
                if collection == "register":
                    if register.find_one({"pubid": hashlib.sha256(pubid.encode()).hexdigest()}):
                        redeem.insert_one({"pubid": hashlib.sha256(pubid.encode()).hexdigest(), "pin": hashlib.sha256(pin.encode()).hexdigest()})
                        register.delete_one({"pubid": hashlib.sha256(pubid.encode()).hexdigest()})
                        return "Submit", True, None, None, None, None, False, True,"you have successfully created your secret PIN", "success", "REGISTRATION SUCCESSFUL"
                elif collection == "redeem":
                    if redeem.find_one({"pubid": hashlib.sha256(pubid.encode()).hexdigest(), "pin": hashlib.sha256(pin.encode()).hexdigest()}):
                        details.insert_one({"name": name, "email": email})
                        redeem.delete_one({"pubid": hashlib.sha256(pubid.encode()).hexdigest(), "pin": hashlib.sha256(pin.encode()).hexdigest()})
                        return "Submit", True, None, None, None, None, False, True, "we will process your request within 10 working days", "success", "REDEMPTION SUCCESSFUL"
        except Exception as e:
            return "Submit", True, None, None, None, None, False, True, str(e), "danger", "ERROR"
        return "Submit", True, None, None, None, None, False, True, "you have entered wrong cerdentials or these credentials have already been used", "info", "FAILED"
    
@app.callback(
    Output("instruction", "children"),
    Output("checkbox", "label"),
    Output("checkbox", "value"),
    Output("name-div", "style"),
    Output("email-div", "style"),
    [Input("collection", "value")],
)
def update_instructions(value):
    if value == "register":
        return html.P("Please create a four-digit PIN", style={"fontSize": "12px"}), html.P("I accept all terms and conditions from the issuer and have safely stored my PIN", style={"fontSize": "12px"}), False, {"display": "none"}, {"marginTop": "10px", "display": "none"}
    return html.P("Please provide the four-digit PIN you created during the registration process", style={"fontSize": "12px"}), html.P("I agree to providing correct contact information and understand that this action is irreversible", style={"fontSize": "12px"}), False, {"display": "block"}, {"marginTop": "10px", "display": "block"}

@app.callback(
    Output("navbar-collapse", "is_open"),
    [Input("navbar-toggler", "n_clicks")],
    [State("navbar-collapse", "is_open")],
)
def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

if __name__ == '__main__':
    app.run_server()
