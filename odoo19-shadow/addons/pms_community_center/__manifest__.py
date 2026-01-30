{
    'name': 'PMS Community Center (CC)',
    'version': '1.0',
    'summary': 'Happiness Coins, Vouchers, and Volunteer Delivery Hub',
    'category': 'Community',
    'author': 'Wuchang Little J (Double J Architecture)',
    'depends': ['base', 'website'],
    'data': [
        'security/ir.model.access.csv',
        'views/voucher_views.xml',
        'views/delivery_views.xml',
    ],
    'installable': True,
    'application': True,
}
