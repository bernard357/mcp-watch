
#
# General pump settings
#

pump = {

    # set to True if you need more details on execution
    #
    'debug': False,

    # regions to be analysed
    #
    # 'regions': ['dd-af', 'dd-ap', 'dd-au', 'dd-eu', 'dd-na'],

    # should better be set in computer environment
    #
    # 'MCP_USER': 'foo.bar',

    # should better be set in computer environment
    #
    # 'MCP_PASSWORD': 'WhatsUpDoc',

    }

#
# file settings -- activate to store data in local files
#

files = {
    'active': False,
    'summary_usage': './logs/summary_usage.log',
    'detailed_usage': './logs/detailed_usage.log',
    'audit_log': './logs/audit_log.log',
    }

#
# InfluxDB settings -- activate to store time series
#

influxdb = {
    'active': False,
    'host': 'localhost',
    'port': 8086,
    'user': 'root',
    'password': 'root',
    'database': 'mcp',
    }

#
# Qualys settings -- activate to scan cloud servers
#

qualys = {
    'active': False,
    'url': 'https://qualysguard.qualys.eu/',
    'login': '$QUALYS_LOGIN',
    'password': '$QUALYS_PASSWORD',
    'option': 'EBC Feb 2017',
    }

