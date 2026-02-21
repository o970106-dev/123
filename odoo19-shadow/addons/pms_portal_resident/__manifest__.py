{
    'name': 'PMS Resident Portal',
    'version': '1.0',
    'category': 'Property Management',
    'summary': 'Glassmorphism dashboard for residents',
    'depends': ['pms_community_center', 'website'],
    'data': [
        'views/portal_templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'pms_portal_resident/static/src/css/portal.css',
            'pms_portal_resident/static/src/js/pms_telemetry.js',
        ],
    },
    'installable': True,
}
