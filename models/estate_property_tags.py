from odoo import models, fields
from random import randint

class EstatePropertyTags(models.Model):
    _name = 'estate.property.tags'
    _description = 'Estate Property Tags'
    _order = 'name asc'

    name = fields.Char(
        required=True
    )
    
    color = fields.Integer(
        default=lambda self: randint(1, 11),
        help="Color index for the tag"
    )

    active = fields.Boolean(
        default=True,
        help="Is the tag active?"
    )
    
    _name_unique = models.Constraint(
        'unique(name)',
        "The tag name must be unique.",
    )