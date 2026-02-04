{
    'name': 'PMS Resident Portal',
    'version': '1.0',
    'author': 'Double J Authority',
    'license': 'LGPL-3',
    'depends': ['base', 'website', 'pms_community_center', 'pms_base'],
    'data': [
        'security/ir.model.access.csv',
        'views/templates.xml'
    ],
    'assets': {
        'web.assets_frontend': [
            'pms_portal_resident/static/src/js/pms_toggle.js',
        ],
    }
}
