
from odoo import fields, models, api
from datetime import datetime, timedelta
from odoo.exceptions import UserError

class EstatePropertyOffer(models.Model):
    _name = 'estate.property.offer'
    _description = 'Real Estate Property Offer'
    _order = 'price desc'

    price = fields.Float(string="Price", required=True)
    validity = fields.Integer(string="Validity (Days)", default=7)
    date_deadline = fields.Date(string="Deadline Date", compute="_compute_date_deadline", inverse="_inverse_date_deadline")
    property_id = fields.Many2one('estate.property', string="Property")
    description = fields.Char(compute="_compute_description", store=True)
    partner_id = fields.Many2one("res.partner")
    total = fields.Float(compute="_compute_total", inverse="_inverse_total")
    amount = fields.Float()

    state = fields.Selection(
        selection=[
            ('new', 'New'),
            ('offer_received', 'Offer Received'),
            ('offer_accepted', 'Offer_Accepted'),
            ('refused', 'Refused'),  # Pastikan nilai ini ada
            ('sold', 'Sold'),
            ('canceled', 'Canceled'),
        ],
        string="Status",
        compute="_compute_state",
        store=True,
    )
    
    @api.depends('property_id.state')
    def _compute_state(self):
        for offer in self:
            offer.state = offer.property_id.state

    @api.depends('create_date', 'validity')
    def _compute_date_deadline(self):
        for offer in self:
            if offer.create_date:
                deadline_date = offer.create_date + timedelta(days=offer.validity)
                offer.date_deadline = deadline_date.date()
            else:
                offer.date_deadline = False

    def _inverse_date_deadline(self):
        for offer in self:
            if offer.date_deadline:
                if offer.create_date:
                    create_date_date = offer.create_date.date()
                    offer.validity = (offer.date_deadline - create_date_date).days
                else:
                    offer.validity = 7  # Default value if create_date is missing
            else:
                offer.validity = 7   # Default value if date_deadline is missing

    @api.depends("amount")
    def _compute_total(self):
        for record in self:
            record.total = 2.0 * record.amount

    def _inverse_total(self):
        for record in self:
            record.amount = record.total / 2.0

    @api.depends("partner_id.name")
    def _compute_description(self):
        for record in self:
            record.description = "Test for partner %s" % record.partner_id.name

    # Actions
    def action_accept(self):
        for offer in self:
            if offer.state == 'offer_accepted':
                raise UserError("This offer has already been accepted.")
            
            # Update the offer state
            offer.state = 'offer_accepted'
            
            # Update the related property state
            offer.property_id.state = 'offer_accepted'
            offer.property_id.selling_price = offer.price  # Set the selling price
            offer.property_id.buyer_id = offer.partner_id  # Set the buyer

    def action_refuse(self):
        for offer in self:
            offer.state = 'refused'

    def action_sold(self):
        for property in self:
            if property.state == 'canceled':
                raise UserError("Canceled properties cannot be sold.")
            property.state = 'sold'