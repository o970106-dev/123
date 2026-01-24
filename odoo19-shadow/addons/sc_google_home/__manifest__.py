{
    'name': 'Smart Control: Google Home Integration',
    'version': '1.0',
    'category': 'Services/SmartControl',
    'summary': 'Connects PMS IoT devices to Google Home ecosystem',
    'description': """
        This module provides a Google Home fulfillment endpoint to control IoT devices.
        Features:
        - Bearer token validation
        - SYNC, QUERY, EXECUTE intents
        - Support for OnOff, Brightness, ColorTemperature, and TemperatureSetting traits.
    """,
    'author': 'SmartControl-PMS Authority',
    'depends': ['base'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/device_views.xml',
        'data/sc_demo_data.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
