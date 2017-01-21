
#
# General pump settings
#

pump = {

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
# file settings -- uncomment and edit to store data in local files
#

files = {
    'summary_usage': './logs/summary_usage.log',
    'detailed_usage': './logs/detailed_usage.log',
    'audit_log': './logs/audit_log.log',
    }

#
# InfluxDB settings -- uncomment and edit to store time series
#

influxdb = {
    'host': 'localhost',
    'port': 8086,
    'user': 'root',
    'password': 'root',
    'database': 'mcp',
    }

#
# Qualys settings -- scan cloud servers by setting active to True
#

qualys = {
    'active': False,
    'url': 'https://qualysguard.qualys.eu/',
    'login': '$QUALYS_LOGIN',
    'password': '$QUALYS_PASSWORD',
    }

