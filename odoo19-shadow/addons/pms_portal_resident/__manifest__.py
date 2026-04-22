{
    'name': 'PMS Resident Portal',
    'version': '1.0',
    'category': 'Property Management/Portal',
    'summary': 'High-End Glassmorphism Dashboard for Residents',
    'author': 'Jules',
    'depends': ['portal', 'pms_base', 'pms_community_center', 'sc_google_home'],
    'data': [
        'views/portal_templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'pms_portal_resident/static/src/css/portal_glass.css',
            'pms_portal_resident/static/src/js/pms_telemetry.js',
        ],
    },
    'installable': True,
}
