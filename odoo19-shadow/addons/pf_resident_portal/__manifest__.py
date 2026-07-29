{
    'name': 'Property Facility: Resident Portal',
    'version': '1.0',
    'category': 'Services/Property',
    'summary': 'Unified resident portal for PMS services',
    'description': """
        Provides a dedicated dashboard for residents to manage:
        - Facility bookings
        - Package notifications
        - Smart home controls
        - Billing and announcements
    """,
    'author': 'SmartControl-PMS Authority',
    'depends': ['portal', 'website'],
    'data': [
        'views/portal_templates.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
