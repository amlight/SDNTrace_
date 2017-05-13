Web configuration
=================

1. Put the files on ``/var/www/html`` or wherever is your DocumentRoot.
2. Insert the following to you Virtual Host configuration::

    RewriteEngine On
    RewriteRule ^/sdntrace(.*) http://<your controller>/sdntrace$1 [P]

3. Enable the following Apache modules::

    proxy
    proxy_http
    rewrite



# Testing the SDN trace
You can use a Firefox Rest plugin to test the trace response.
Send a PUT request to:

    http://127.0.0.1:8182/sdntrace/trace

Send a json mime type data:
    {"trace":{"switch":{"dpid":"0000000000000001","in_port":1},"eth":{"dl_vlan":100}}}
