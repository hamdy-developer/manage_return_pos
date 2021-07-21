# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, exceptions
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError


class pos_exchan(models.Model):
    _inherit = 'pos.order.line'
    _description = 'POS exchange products'

    chek_box = fields.Boolean(string='box')
    themain_qty = fields.Float(string='main qty')

    def _prepare_refund_data(self, refund_order, PosOrderLineLot):
        """
        This prepares data for refund order line. Inheritance may inject more data here

        @param refund_order: the pre-created refund order
        @type refund_order: pos.order

        @param PosOrderLineLot: the pre-created Pack operation Lot
        @type PosOrderLineLot: pos.pack.operation.
            # refund_order_line.field_name=refund_order_line.qty

        if refund_order_line.qty >= 0:
            refund_order_line.sudo().unlink()
            order = self.env['pos.order'].search([('id', '=', refund_orders.ids[0])])
            order.sudo()._onchange_amount_all()

    pos_order = self.env['pos.order'].search([('id', '=', refund_orders.ids[0])])
    if not pos_order.lines:
        raise ValidationError(_("you can't return it"))lot

        @return: dictionary of data which is for creating a refund order line from the original line
        @rtype: dict
        """
        self.ensure_one()
        orders = self.env['pos.order'].search([('name', '=', self.order_id.name + _(' REFUND')),
                                               ('id', '!=', refund_order.id),
                                               ('state', 'not in', ('draft', 'cancel'))])
        lines = self.env['pos.order.line'].search(
            [('order_id', 'in', orders.ids), ('product_id', '=', self.product_id.id)])

        return {
            'name': self.name + _(' REFUND'),
            'qty': -(self.qty + sum(lines.mapped('qty'))),
            'chek_box': True,
            'order_id': refund_order.id,
            'price_subtotal': -self.price_subtotal,
            'price_subtotal_incl': -self.price_subtotal_incl,
            'pack_lot_ids': PosOrderLineLot,
            'themain_qty': -(self.qty + sum(lines.mapped('qty'))),
        }

    @api.constrains('themain_qty', 'qty')
    def constrains_qty(self):
        for rec in self:
            if rec.chek_box == True:
                if rec.qty > 0:
                    raise ValidationError(_("you cann't sell from here"))
                if rec.qty < rec.themain_qty:
                    raise ValidationError(_("you cann't return more than %s" % -rec.themain_qty))


#
class pos_order(models.Model):
    _inherit = 'pos.order'

    def refund(self):
        res = super(pos_order, self).refund()
        order = self.search([('id', '=', res.get('res_id', False))])
        for rec in order:
            for line in rec.lines:
                line._onchange_qty()
                if line.qty == 0:
                    line.sudo().unlink()
            if not rec.lines:
                raise ValidationError(_("you can't return it"))
            rec._onchange_amount_all()
        return res
