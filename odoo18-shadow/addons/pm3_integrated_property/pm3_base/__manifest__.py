{
    'name': 'PM3 Base',
    'version': '18.0.1.0.0',
    'summary': 'Base menu, shared governance constants, and PM3 runtime foundation.',
    'category': 'Services/Property',
    'license': 'LGPL-3',
    'depends': ['base', 'mail'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/pm3_menu.xml',
        'views/pm3_base_config_views.xml',
    ],
    'installable': True,
    'application': True,
}
