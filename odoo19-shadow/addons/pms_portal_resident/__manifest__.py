{
    'name': 'PMS Portal Resident (PF Node)',
    'version': '19.0.2.0',
    'summary': 'High-end Glassmorphism Resident Dashboard',
    'depends': ['pms_base', 'pms_community_center', 'website'],
    'data': [
        'views/templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'pms_portal_resident/static/src/js/pms_telemetry.js',
        ],
    },
    'category': 'Property Management',
    'license': 'OEEL-1',
}
