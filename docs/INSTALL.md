# Installation

SDNTrace is composed of two different applications: a controller, which runs the actual trace and is accessed through a RESTful interface, and a web interface allowing the user to easily interact with the software.
An instance of the contoller must be initiated in each domain that will run traces. One or more instances of the web interface can be initiated.
Both the contoller and the web interface have configuration files.

## Controller configuration

Controller configuration is composed of several sections. They are described above.

### [general]
`debug = [False|True]` - start in debug mode, default to `False`  
`log-file = filename` - log file name, default to `sdntrace.log`

### [openflow]
`version = 1.0` - OpenFlow version  
`minimum_cookie_id = 2000000`

### [trace]
`color_field = dl_src` - OpenFlow field to be used for coloring, default to `dl_src`  
`push_color_interval = 10` -   
`flow_priority = 50000` - priority of the color flows, default to `50000`  
`run_trace_interval = 1`

### [ryu]
`listen_port = 6633` - port Ryu will listen for switch connections, default to `6633`  
`wsgi_port = 8000` - port Ryu listen for HTTP REST requests, default to `8000`

### [apps]
`load = app1,app2` - apps to be loaded, default to None

## Execute the controller

To run the controller, enter the directory where SDNTrace is installed and type the following command:
    
    python run.py --config-file <controller-configuration-file>
    
## Web interface configuration

The web interface configuration is composed of just one section

### [web-rest]
`REST_HOST = localhost` - host where te controller is serving its REST API, defaults to `localhost`  
`REST_PORT = 8000` - port the controller uses to serve REST API, defaults to K 8000ˋ