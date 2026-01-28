{
    'name': 'Smart Control: Google Home Integration',
    'version': '1.0',
    'category': 'Property Management/Smart Control',
    'summary': 'Integration with Google Home for device synchronization and control',
    'description': 'Provides a fulfillment endpoint for Google Home and Odoo models for smart devices.',
    'depends': ['base', 'pms_base'],
    'data': [
        'security/ir.model.access.csv',
        'views/device_views.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
