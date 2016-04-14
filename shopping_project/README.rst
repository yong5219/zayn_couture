To use PyMySQL, patch the following code in manage.py

    try:
        import pymysql
        pymysql.install_as_MySQLdb()
    except ImportError:
        pass


To setup database

    CREATE DATABASE malay_shopping_dev character set utf8 COLLATE utf8_general_ci;

    GRANT ALL PRIVILEGES ON `malay_shopping_dev`.* TO 'malay_shopping'@'localhost' IDENTIFIED BY 'malayshoppingpass' WITH GRANT OPTION;

    FLUSH PRIVILEGES;


Install python lib on webfaction

    pip3.4 install --install-option="--install-scripts=$PWD/bin" --install-option="--install-lib=$PWD/lib/python3.4" --user package

    pip3.4 install --upgrade --install-option="--install-scripts=$PWD/bin" --install-option="--install-lib=$PWD/lib/python3.4" --user package


For Python 3

    Just use __str__(). no more __unicode__().


For server's configuration

    in wsgi.py's level __init__.py add the following codes:

    try:
        import pymysql
        pymysql.install_as_MySQLdb()
    except ImportError:
        pass
