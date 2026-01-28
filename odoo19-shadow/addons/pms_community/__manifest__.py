{
    'name': 'PMS Community & AI Service',
    'version': '1.0',
    'category': 'Property Management/Community',
    'summary': 'AI Service Node (物管小J) and Community Chat for Renyi District',
    'depends': ['base', 'pms_base', 'website'],
    'data': [
        'security/ir.model.access.csv',
        'data/knowledge_data.xml',
        'views/knowledge_views.xml',
        'views/chat_views.xml',
        'views/community_templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'pms_community/static/src/js/community_chat.js',
        ],
    },
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
