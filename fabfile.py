# -*- coding: utf-8 -*-
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import with_statement
from fabric.api import *


def restart_apache_dev():
    sudo("service apache2 restart")


def deploy_dev():
    run('mkdir -p /home/mininet/SDNTrace/')

    put('/projetos/SDNTrace/*.py', '/home/mininet/SDNTrace/')
    put('/projetos/SDNTrace/web/', '/home/mininet/SDNTrace/')

    run('mkdir -p /home/mininet/SDNTrace/docs/')
    put('/projetos/SDNTrace/docs/*', '/home/mininet/SDNTrace/docs/')

    run('mkdir -p /home/mininet/SDNTrace/libs/')
    put('/projetos/SDNTrace/libs/*.py', '/home/mininet/SDNTrace/libs/')

    run('mkdir -p /home/mininet/SDNTrace/libs/Coloring/')
    put('/projetos/SDNTrace/libs/Coloring/*.py', '/home/mininet/SDNTrace/libs/Coloring/')

    run('mkdir -p /home/mininet/SDNTrace/libs/Exceptions/')
    put('/projetos/SDNTrace/libs/Exceptions/*.py', '/home/mininet/SDNTrace/libs/Exceptions/')

    run('mkdir -p /home/mininet/SDNTrace/libs/Tracing/')
    put('/projetos/SDNTrace/libs/Tracing/*.py', '/home/mininet/SDNTrace/libs/Tracing/')

    run('mkdir -p /home/mininet/SDNTrace/libs/Statistics/')
    put('/projetos/SDNTrace/libs/Statistics/*.py', '/home/mininet/SDNTrace/libs/Statistics/')

    sudo('cp /home/mininet/SDNTrace/web/html/*.* /var/www/html/')

    sudo('mkdir -p /var/www/html/lib/')
    sudo('cp /home/mininet/SDNTrace/web/html/lib/*.* /var/www/html/lib/')

    sudo('mkdir -p /var/www/html/fonts/')
    sudo('cp /home/mininet/SDNTrace/web/html/fonts/*.* /var/www/html/fonts/')

    # parando o apache para modificar os arquivos do sistema
    sudo("service apache2 restart")

    # removendo os arquivos python binários, para não ter problema com arquivos removidos
    # run("rm -rf /var/lib/sistema/*.pyc")

    # reiniciando o apache
    # sudo("service apache2 start")



"""
 Definição da localização do host
 O usuáriorio deve digitar a senha de acesso.

 Uso:
     fab dev
     fab production
"""
def dev():
    env.hosts = ['10.0.0.51']
    env.user = 'mininet'

