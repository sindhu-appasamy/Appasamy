# -*- coding: utf-8 -*-
import base64
from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from odoo.addons.report_base.controllers.main import ExcelExport

class DailyReportExport(models.TransientModel):
    _name = 'daily.report.export'
    _description = 'Daily Report'

    start_date = fields.Date(string='Start Date', required=True)
    end_date = fields.Date(string='End Date', required=True)
    categ_id = fields.Many2one('product.category', string='Category')
    pending_group_by = fields.Boolean(string='Overall Pending',default = True,readonly=1)

    def action_print(self):
        DailyReport = self.env['daily.report']

        domain = [
            ('date', '>=', self.start_date),
            ('date', '<=', self.end_date)
        ]
        
        value_list = []
        if self.categ_id:
            domain += [('categ_id', '=', self.categ_id.id)]
       
        records = DailyReport.search(domain)

        if self.pending_group_by:
            res = {}
            for rec in records:
                if rec.company_id.id not in res:
                    res[rec.company_id.id] = {}
                if rec.company_id.id in res and rec.product_id.id not in res[rec.company_id.id]:
                    res[rec.company_id.id][rec.product_id.id] = {
                        'Start Date': rec.date,
                        'End Date': rec.date,
                        'Company': rec.company_id.name,
                        'Product Name': rec.product_id.name,
                        'Category': rec.categ_id.name or '',
                        'Production Qty': 0,
                        'Todays Production': 0,
                        'Inward Qty': 0,
                        'Todays Inward': 0,
                        'Outward Qty': 0,
                        'Todays Outward': 0,
                        'Return Qty': 0,
                        'Todays Return': 0,
                        'Pending Qty': 0,
                        }
                #if rec.date >= res[rec.company_id.id][rec.product_id.id]['Start Date']:
                res[rec.company_id.id][rec.product_id.id]['Pending Qty'] += rec.pending_qty
                res[rec.company_id.id][rec.product_id.id]['Todays Production'] += rec.today_production
                res[rec.company_id.id][rec.product_id.id]['Todays Inward'] += rec.today_inward
                res[rec.company_id.id][rec.product_id.id]['Todays Outward'] += rec.today_outward
                res[rec.company_id.id][rec.product_id.id]['Todays Return'] += rec.today_return
                #if res[rec.company_id.id][rec.product_id.id]['Start Date'] >= rec.date <= res[rec.company_id.id][rec.product_id.id]['End Date']:
                res[rec.company_id.id][rec.product_id.id]['Production Qty'] += rec.production_qty
                res[rec.company_id.id][rec.product_id.id]['Inward Qty'] += rec.inward_qty
                res[rec.company_id.id][rec.product_id.id]['Outward Qty'] += rec.outward_qty
                res[rec.company_id.id][rec.product_id.id]['Return Qty'] += rec.return_qty
            
            field_list = [
                        'Start Date', 'End Date', 'Company', 'Product Name', 'Category', 'Production','Todays Production',
                        'Inward Qty', 'Todays Inward', 'Outward Qty', 'Todays Outward', 'Return Qty', 'Todays Return',
                        'Pending Qty'
                        ]
            for res_dict in res.values():
                for record in res_dict.values():
                    start_date = datetime.strptime(fields.Date.to_string(self.start_date), DEFAULT_SERVER_DATE_FORMAT).date() if self.start_date else ''
                    end_date = datetime.strptime(fields.Date.to_string(self.end_date), DEFAULT_SERVER_DATE_FORMAT).date() if self.end_date else ''
                    value_list.append([
                        start_date, end_date, record.get('Company'), record.get('Product Name'), record.get('Category'),
                        record.get('Production Qty'), record.get('Todays Production'),record.get('Inward Qty'), record.get('Todays Inward'),
                        record.get('Outward Qty'), record.get('Todays Outward'), record.get('Return Qty'),  record.get('Todays Return'),
                        record.get('Pending Qty')
                        ])

        obj = ExcelExport()
        data = obj.from_data(field_list, value_list)

        values = {
            'name': "Daily Report.xls",
            'res_model': 'ir.ui.view',
            'res_id': False,
            'type': 'binary',
            'public': True,
            'datas': base64.b64encode(data),
        }

        attachment_id = self.env['ir.attachment'].sudo().create(values)

        download_url = '/web/content/' + str(attachment_id.id) + '?download=True'
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')

        return {
            "type": "ir.actions.act_url",
            "url": str(base_url) + str(download_url),
            "target": "new",
        }