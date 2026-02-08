{
    'name': 'Smart Control: Google Home Integration (Double J)',
    'version': '3.0.0',
    'summary': 'High-performance Google Home Integration with STAPS O(1) Telemetry',
    'category': 'Services/PMS',
    'author': 'PMS Authority',
    'depends': ['base', 'web', 'pms_base'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/device_views.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
