{
    'name': 'Resident Portal: Optimized Dashboard',
    'version': '1.0',
    'category': 'Property Management/Portal',
    'summary': 'High-end resident portal with glassmorphism UI and real-time telemetry',
    'description': 'Provides a modern interface for residents to manage their property and smart devices.',
    'depends': ['website', 'sc_google_home', 'pms_base'],
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
