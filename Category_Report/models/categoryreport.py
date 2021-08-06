# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo import tools

class Field(models.Model):
	_name = "category.report"
	_auto = False
	_description = "Category report"

	partner_id = fields.Many2one('res.partner',string='Customer')
	division_id = fields.Many2one('res.partner.division',string='Division')
	branch_id = fields.Many2one('res.partner.branch',string='Branch')
	invoice_ids = fields.Many2one('account.move',string='Invoices')
	name_id = fields.Char(string='Invoice Number')
	inv_date = fields.Date(string='Invoice Date')
	product_id = fields.Many2one('product.product',string='Product Name')
	categ_id =fields.Many2one('product.category',string='Product Category')
	product_sub_category_id =fields.Many2one('product.template.sub.category',string='Product SubCategory')
	product_category_id = fields.Many2one('product.category',string='Order Category')
	amount_untaxed = fields.Float(string='Untaxed Amount', group_operator='max')
	amount_tax = fields.Float(string='Tax Amount', group_operator='max')
	amount_total = fields.Float(string='Total Amount', group_operator='max')
	payment_ids =  fields.Many2one('account.move.line',string='Payment Reference')
	payment_amount =fields.Float(string='Allocation Amount')
	payment_date = fields.Date(string='Payment Date')
	company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)

	def _select(self):	
		return """
			SELECT 
				row_number() over(ORDER BY acc.invoice_date desc, acc.name, aml.product_id desc) as id,
				acc.name as name_id,
				acc.id as invoice_ids,
				acc.product_category_id as product_category_id,
				acc.invoice_date as inv_date,
				aml.product_id as product_id,
				pt.categ_id as categ_id,
				pt.product_sub_category_id as product_sub_category_id,
				CASE
				    WHEN aml.product_id is Null THEN acc.amount_untaxed
					ELSE aml.price_subtotal
				END as amount_untaxed,
				CASE
					WHEN aml.product_id is Null THEN acc.amount_tax
					ELSE aml.price_total - aml.price_subtotal
				END as amount_tax,
				CASE
					WHEN aml.product_id is Null THEN acc.amount_total
					ELSE aml.price_total
				END as amount_total,
				acc.partner_id as partner_id,
				res.division_id as division_id,
				res.branch_id as branch_id,
				apr.max_date as payment_date,
				apr.credit_move_id as payment_ids,
				apr.amount as payment_amount,
				aml.company_id as company_id
		    """

	def _from(self):
		return """
		FROM account_move_line as aml
		"""

	def _join(self):
        return """
        	LEFT JOIN account_move as acc ON (aml.move_id = acc.id)
			LEFT JOIN account_partial_reconcile as apr ON (apr.debit_move_id = aml.id)
			LEFT JOIN product_product as prt ON (prt.id = aml.product_id)
			LEFT JOIN product_template as pt ON (pt.id = prt.product_tmpl_id) 
			LEFT JOIN res_partner as res ON (res.id = acc.partner_id)
		"""

	def _where(self):
		return"""
		WHERE acc.type = 'out_invoice' AND acc.state = 'posted' AND aml.tax_line_id is null 
		"""

	def _group_by(self):
		return """
		GROUP BY 
			acc.name, acc.id, acc.invoice_date, aml.product_id, acc.partner_id, res.division_id, res.branch_id,
			aml.company_id, acc.product_category_id, pt.categ_id, pt.product_sub_category_id, aml.price_subtotal,
			acc.amount_untaxed, acc.amount_tax, aml.price_total, apr.credit_move_id, apr.amount, apr.max_date
		"""

	def init(self):
		tools.drop_view_if_exists(self._cr, self._table)
		self.env.cr.execute("""
			CREATE OR REPLACE VIEW %s As(
			%s
			%s
			%s
			%s
			%s
			)
		"""% (self._table, self._select(), self._from(), self._join(), self._where(), self._group_by())
		)
