{
    'name': 'Real Estate',
    'version': '0.1',
    'category': 'Sales/CRM',
    'sequence': 1,
    'summary': 'estate',
    'depends': ['base_setup', 'mail', 'calendar', 'sales_team', 'contacts', 'base', 'web'],
    'data': [
        'security/ir.model.access.csv',
        'views/estate_property_views.xml',
        'views/estate_menus.xml',
        'views/estate_property_tag_views.xml',
        'views/estate_property_type_views.xml',
        # 'views/estate_property_offer_views.xml'
        # 'views/estate_property_kanban_views.xml'
    ],
    'demo': [

    ],
    'assets': {
    'web.assets_backend': [
        'real_estate/static/src/css/index.css',
        # 'real_estate/static/src/js/kanban.js',
        ],
    },

    'installable': True,
    'application': True,
    'auto_install': False,
    # 'license': 'LGPL'
}