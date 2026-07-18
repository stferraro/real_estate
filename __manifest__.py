{
    'name': 'Real Estate in Odoo',
    'version': '19.0.1.0.0',
    'summary': 'A Module For Real Estate administration',
    'author': 'Gerardo Alí Ferraro Schelijasch',
    'license': 'LGPL-3',
    'category': 'Other',
    'images': ['static/description/icon.png'],
    'data': [
        #security
        'security/ir.model.access.csv',

        # views and inherit views
        'views/estate_property_views.xml',
        'views/estate_property_type_views.xml',
        'views/estate_property_tags_views.xml',
        'views/estate_property_offer_views.xml',
        'views/res_users_views.xml',

        #menus
        'data/real_estate_menus.xml',
    ],
    'depends': [
        'base',
    ],
    'application': True,
}