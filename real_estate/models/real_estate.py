from odoo import models, fields, api
from datetime import datetime, timedelta
from odoo.exceptions import UserError

class EstateProperty(models.Model):
    _name = 'estate.property'
    _description = 'Real Estate Property'
    _order = 'id desc'

    name = fields.Char(string="Title", default="Unknown", required=True )
    description = fields.Text()
    postcode = fields.Char()
    date_availability = fields.Date(
        string="Available From", 
        copy=False, 
        default=lambda self: (datetime.today() + timedelta(days=90)).date()
    )
    expected_price = fields.Float(required=True)
    selling_price = fields.Float(readonly=True)
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer(string="Living Area (sqm)")
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer(string="Garden Area (sqm)")
    garden_orientation = fields.Selection(
        selection=[('north', 'North'), ('south', 'South'), ('east', 'East'), ('west', 'West')],
    )
    type = fields.Selection([
        ('house', 'House'),
        ('apartment', 'Apartment'),
        ('land', 'Land'),
    ], string='Type')
    active = fields.Boolean(default=True)
    state = fields.Selection(
        selection=[
            ('new', 'New'),
            ('offer_received', 'Offer Received'), 
            ('offer_accepted', 'Offer_Accepted'),
            ('sold', 'Sold'),
            ('canceled', 'Canceled'),
        ],
        string="Status",
        required=True,
        copy=False,
        default='new',
    )
    tag_ids = fields.Many2many('estate.property.tag', string="Tags")

    # New computed field
    tag_names = fields.Char(string="Tag Names", compute="_compute_tag_names", store=True)

    @api.depends('tag_ids.name')
    def _compute_tag_names(self):
        for record in self:
            record.tag_names = ', '.join(record.tag_ids.mapped('name'))
    # Actions
    def action_cancel(self):
        for record in self:
            if record.state == 'sold':
                raise UserError("A sold property cannot be canceled.")
            record.state = 'canceled'

    def action_sold(self):
        for record in self:
            if record.state == 'canceled':
                raise UserError("A canceled property cannot be sold.")
            record.state = 'sold'

    # Existing fields
    property_type_id = fields.Many2one('estate.property.type', string="Property Type")
    buyer_id = fields.Many2one('res.partner', string="Buyer", domain="[('is_company', '=', False)]")
    salesperson_id = fields.Many2one('res.users', string="Salesperson", default=lambda self: self.env.user)
    tag_ids = fields.Many2many('estate.property.tag', string="Tags")
    offer_ids = fields.One2many('estate.property.offer', 'property_id', string="Offers")

    # New computed fields
    total_area = fields.Integer(string="Total Area", compute="_compute_total_area", store=True)
    best_price = fields.Float(string="Best Offer Price", compute="_compute_best_offer", store=True)

    @api.depends('living_area', 'garden_area')
    def _compute_total_area(self):
        for record in self:
            record.total_area = (record.living_area or 0) + (record.garden_area or 0)

    @api.depends('offer_ids.price')
    def _compute_best_offer(self):
        for record in self:
            record.best_price = max(record.offer_ids.mapped('price') or [0.0])

    @api.model
    def create(self, vals):
        # Create a property and change its state to 'Offer Received'
        res = super(EstateProperty, self).create(vals)
        if 'offer_ids' in vals:
            res.state = 'offer_received'
        return res

    def unlink(self):
        for record in self:
            if record.state not in ['new', 'canceled']:
                raise exceptions.UserError("You cannot delete a property unless it is in 'New' or 'Canceled' state.")
        return super(EstateProperty, self).unlink()

    def action_create_offer(self, offer_amount):
        # Ensure the new offer amount is not lower than existing offers
        for record in self:
            if any(offer_amount < offer.offer_amount for offer in record.offer_ids):
                raise exceptions.UserError("The offer amount cannot be lower than existing offers.")
            record.state = 'offer_received'

    