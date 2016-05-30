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

