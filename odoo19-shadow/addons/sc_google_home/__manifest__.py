{
    'name': 'Smart Control - Google Home Integration',
    'version': '19.0.1.0',
    'category': 'Services/SmartControl',
    'summary': 'Integration with Google Home for Property Management',
    'author': 'Wuchang Life',
    'depends': ['base', 'web'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/device_views.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'OEEL-1',
}
