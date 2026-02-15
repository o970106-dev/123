{
    'name': 'PMS Resident Portal (PF)',
    'version': '1.0',
    'summary': 'Resident UI for Happiness Mall and Volunteer Hub',
    'category': 'Website',
    'author': 'Wuchang Little J (Double J Architecture)',
    'depends': ['portal', 'website', 'pms_community_center'],
    'data': [
        'views/portal_templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'pms_portal_resident/static/src/js/pms_telemetry.js',
        ],
    },
    'installable': True,
}
