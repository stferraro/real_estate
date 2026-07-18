from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_compare
from datetime import timedelta

class EstateProperty(models.Model):
    _name = 'estate.property'
    _description = 'Estate Property'
    _order = 'id desc'
    
    name = fields.Char(
        string='Property Name',
        required=True
    )
    
    description = fields.Text(
        help='Description of the property'
    )
    
    active = fields.Boolean(
        default=True,
    )
    
    state = fields.Selection([
        ('new', 'New'),
        ('offer_received', 'Offer Received'),
        ('offer_accepted', 'Offer Accepted'),
        ('sold', 'Sold'),
        ('canceled', 'Canceled')
    ], string="State", default='new')
    
    
    postcode = fields.Char(
        help='Postal Code of the property'
    )

    date_availability = fields.Date(
        help='Date when the property will be available',
        default=fields.Date.today
    )

    expected_price = fields.Float(
        required=True,
        help='Expected selling price of the property'
    )

    selling_price = fields.Float(
        readonly=True,
        copy=False,
        help='Final selling price of the property'
    )

    bedrooms = fields.Integer(
        string='Number of Bedrooms',
        help='The number of bedrooms in the property'
    )

    living_area = fields.Integer(
        string='Living Area (sqm)',
        help='The living area in square meters'
    )

    facades = fields.Integer(
        string='Number of Facades',
        help='The number of facades of the property'
    )

    garage = fields.Boolean(
        help="Whether the property has a garage or not"
    )

    garden = fields.Boolean(
        help="Whether the property has a garden or not"
    )

    garden_area = fields.Integer(
        string='Garden Area (sqm)',
        help="The area of the garden"
    )

    garden_orientation = fields.Selection([
        ('north', 'North'),
        ('south', 'South'),
        ('east', 'East'),
        ('west', 'West')
    ], 
        string='Garden Orientation',
        help='The orientation of the garden'
    )
    
    property_type_id = fields.Many2one(
        comodel_name='estate.property.type',
        string='Property Type',
        help='The type of the property'
    )

    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Currency',
        required=True,
        default=lambda self: self.env.company.currency_id.id,
        help='Currency of the property'
    )

    best_offer = fields.Monetary(
        string='Best Offer',
        currency_field='currency_id',
        compute='_compute_best_offer',
        help='The highest offer received for the property'
    )

    buyer_id = fields.Many2one(
        comodel_name='res.partner',
        string='Buyer', 
        ondelete='restrict',
        help='The buyer of the property'
    )
    
    salesperson_id = fields.Many2one(
        comodel_name='res.users',
        string='Salesperson',
        ondelete='restrict',
        default=lambda self: self.env.user.id,
        help='The salesperson responsible for this property'
    )
    
    tags_ids = fields.Many2many(
        comodel_name='estate.property.tags',
        string='Tags',
        help='Tags associated with the property'
    )
    
    total_area = fields.Integer(
        string='Total Area (sqm)',
        compute='_compute_total_area',
        help='Total area of the property including garden'
    )
    
    offers_ids = fields.One2many(
        comodel_name='estate.property.offer',
        inverse_name='property_id',
        string='Offers',
        help='Offers made for this property'
    )

    @api.depends('living_area', 'garden_area')
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area
            
    @api.depends('offers_ids.price')
    def _compute_best_offer(self):
        for record in self:
            if record.offers_ids:
                record.best_offer = max(record.offers_ids.mapped('price'))
                record.selling_price = record.best_offer
            else:
                record.best_offer = 0.0

    def action_sold(self):
        if self.filtered(lambda p: p.state == 'canceled'):
            raise UserError("Canceled properties cannot be sold.")
        self.write({'state': 'sold'})
        return True

    def action_cancel(self):
        if self.filtered(lambda p: p.state == 'sold'):
            raise UserError("Sold properties cannot be canceled.")
        self.write({'state': 'canceled'})
        return True
    
    @api.constrains('selling_price', 'expected_price', 'offers_ids')
    def _check_selling_price(self):
        for rec in self:
            if len(rec.offers_ids) > 1:
                if float_compare(
                        rec.selling_price, rec.expected_price * 0.9, precision_digits=2) == -1:
                    raise ValidationError(_("The selling price can't be lower than 90% of the expected price."))
            elif len(rec.offers_ids) == 0 and rec.selling_price != 0:
                raise ValidationError(_("The selling price must be 0 if there are no offers."))

    @api.ondelete(at_uninstall=False)
    def _unlink_if_new_or_canceled(self):
        for record in self:
            if record.state not in ('new', 'canceled'):
                raise UserError("Only properties in 'new' or 'canceled' state can be deleted.")

    _expected_price_positive = models.Constraint(
        'CHECK(expected_price > 0)',
        "The expected price must be positive.",
    )
    _selling_price_positive = models.Constraint(
        'CHECK(selling_price >= 0)',
        "The selling price must be non-negative.",
    )
    _selling_price_less_equal_expected = models.Constraint(
        'CHECK(selling_price <= expected_price)',
        "The selling price cannot exceed the expected price.",
    )
            
class EstatePropertyOffer(models.Model):
    _name = 'estate.property.offer'
    _description = 'Estate Property Offer'
    _order = 'price desc'

    price = fields.Float(
        required=True,
        help='Offered price for the property'
    )
    
    state = fields.Selection([
        ('accepted', 'Accepted'),
        ('refused', 'Refused')
    ], 
        string='Status',
        help='Status of the offer'
    )

    validity = fields.Integer(
        default=7,
        help='Number of days the offer is valid'
    )

    deadline_date = fields.Datetime(
        compute='_compute_deadline',
        string='Deadline',
        help='Deadline for the offer'
    )

    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Partner',
        required=True,
        help='The partner making the offer'
    )
    
    property_id = fields.Many2one(
        comodel_name='estate.property',
        string='Property',
        required=True,
        help='The property for which the offer is made'
    )

    property_type_id = fields.Many2one(
        related='property_id.property_type_id',
        string='Property Type',
        store=True,
        help='The type of the property'
    )

    def action_accept(self):
        for offer in self:
            min_price = offer.property_id.expected_price * 0.9
            if offer.price < min_price:
                raise ValidationError(_("The selling price can't be lower than 90% of the expected price."))
            
            offer.write ({'state': 'accepted'})

            offer.property_id.write({
                'selling_price': offer.price,
                'buyer_id': offer.partner_id.id,
                'state': 'offer_accepted'
            })

            other_offers = self.search([
                ('property_id', '=', offer.property_id.id),
                ('id', '!=', offer.id)
            ])
            other_offers.write({'state': 'refused'})

    def action_refuse(self):
        self.write({'state': 'refused'})
        return True

    def _compute_deadline(self):
        for record in self:
            if record.create_date:
                record.deadline_date = record.create_date + timedelta(days=record.validity)
            else:
                record.deadline_date = fields.Datetime.now() + timedelta(days=record.validity)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            property_id = self.env['estate.property'].browse(vals.get('property_id'))
            offer_ids = property_id.offers_ids
            if offer_ids and vals['price'] < max(offer_ids.mapped('price'), default=0):
                raise UserError("A new can't be have a lower price than the highest current offer.")
            elif not offer_ids:
                property_id.write({'state': 'offer_received'})
        return super(EstatePropertyOffer, self).create(vals_list)



