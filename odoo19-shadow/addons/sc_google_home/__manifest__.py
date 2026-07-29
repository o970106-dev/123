{
    'name': 'Smart Control: Google Home Integration',
    'version': '2.0.0',
    'summary': 'Integration with Google Home for Smart Property Management',
    'category': 'Services/PMS',
    'author': 'PMS Authority',
    'depends': ['base', 'web'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/device_views.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
