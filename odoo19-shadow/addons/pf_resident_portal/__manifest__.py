{
    'name': 'Resident Portal (Home)',
    'version': '1.0',
    'category': 'Property Management',
    'summary': 'A beautiful home for residents of Wuchang.',
    'description': 'Provides a unified dashboard for residents to manage their home.',
    'depends': ['portal', 'account'],
    'data': [
        'views/portal_templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'pf_resident_portal/static/src/css/portal.css',
        ],
    },
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
