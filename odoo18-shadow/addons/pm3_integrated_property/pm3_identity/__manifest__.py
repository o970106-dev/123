{
    'name': 'PM3 Identity',
    'version': '18.0.1.0.0',
    'summary': 'Five-dimensional identity governance and credential runtime.',
    'category': 'Services/Property',
    'license': 'LGPL-3',
    'depends': ['pm3_base', 'contacts', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/pm3_identity_views.xml',
    ],
    'installable': True,
    'application': False,
}
