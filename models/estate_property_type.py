from odoo import models, fields, _

class EstatePropertyType(models.Model):
    _name = 'estate.property.type'
    _description = 'Estate Property Type'
    _order = 'sequence'

    sequence = fields.Integer(
        default=1,
        help="Sequence for ordering property types"
    )

    name = fields.Char(
        required=True
    )

    property_ids = fields.One2many(
        'estate.property',
        'property_type_id',
        string='Properties',
        help='Properties of this type'
    )

    offer_ids = fields.One2many(
        'estate.property.offer',
        'property_type_id',
        string='Offers',
        help='Offers for properties of this type'
    )

    offer_count = fields.Integer(
        compute='_compute_offer_count',
        string='Offer Count',
        help='Number of offers for properties of this type'
    )

    _name_unique = models.Constraint(
        'unique(name)',
        "The property type name must be unique.",
    )

    def _compute_offer_count(self):
        for rec in self:
            rec.offer_count = len(rec.offer_ids)

    def action_open_offer_ids(self):
        self.ensure_one()
        return {
            'name': _('Offers',),
            'type': 'ir.actions.act_window',
            'view_mode': 'list,form',
            'res_model': 'estate.property.offer',
            'domain': [('property_type_id', '=', self.id)],
            'context': {'default_property_type_id': self.id},
        }
    
    