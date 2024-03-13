# -*- coding: utf-8 -*- © 2017 Carlos R. Silveira, ATSti
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from datetime import date, datetime
from odoo.exceptions import UserError

class AccountMove(models.Model):
    _inherit = 'account.move'
    
    parcela_ids = fields.One2many(
        'invoice.parcela', 'move_id',
        string=u"Parcelas")
    num_parcela = fields.Integer('Núm. Parcela')
    dia_vcto = fields.Integer('Dia Vencimento', default=0)
    # rateio_frete = fields.Boolean('Rateio do Frete', default=False)
    vlr_prim_prc = fields.Float('Valor Prim. Parcela', default=0.0)
    payment_mode_id = fields.Many2one(
       'account.payment.mode', string=u"Modo de pagamento")
    
    # TODO saindo o mesmo nome para todas as parcelas

    # def action_post(self):
    #     import pudb;pu.db
    #     different = False
    #     if self.num_parcela > 0:
    #         self.invoice_payment_term_id = False
    #         res = super().action_post()
    #         self.action_confirma_parcela()
    #     else:
    #         return super().action_post()
    #     for prc in self.parcela_ids:
    #         fin = self.financial_move_line_ids.filtered(lambda l: l.date_maturity == prc.data_vencimento)
    #         if self.move_type == "in_invoice":
    #             if fin.credit != prc.valor:
    #                 different = True
    #                 break
    #         if self.move_type == "out_invoice":
    #             if fin.debit != prc.valor:
    #                 different = True
    #                 break
    #     if different:
    #         raise UserError(_(f"Parcela não foi confirmada, favor confirmar na aba PARCELAS.")) 

    #     return res
 
    def action_confirma_parcela(self):
        import pudb;pu.db
        if self.num_parcela > 0:
            account = self.financial_move_line_ids[0].account_id
            self.financial_move_line_ids.with_context(check_move_validity=False).unlink()
            date_due = False
            for prc in self.parcela_ids:
                create_method = self.env['account.move.line'].with_context(check_move_validity=False).create
                valor_cre = 0
                valor_deb = 0
                if self.move_type == "in_invoice":
                    valor_cre = prc.valor
                if self.move_type == "out_invoice":
                    valor_deb = prc.valor
                if not self.payment_reference:
                    name_line = f"{self.payment_reference}-{prc.numero_fatura}"
                else:
                    name_line = f"{self.payment_reference}-{prc.numero_fatura}"
                create_method({
                        'name': name_line,
                        'debit': valor_deb,
                        'balance': prc.valor,
                        'credit': valor_cre,
                        'quantity': 1.0,
                        'amount_currency': prc.valor,
                        'date_maturity': prc.data_vencimento,
                        'move_id': self.id,
                        'currency_id': self.currency_id.id,
                        'account_id': account.id,
                        'partner_id': self.commercial_partner_id.id,
                        'exclude_from_invoice_tab': True,
                })
                date_due = prc.data_vencimento
            if date_due:
                self.invoice_date_due = date_due
   
    def calcular_vencimento(self, dia_preferencia, parcela):
        import pudb;pu.db
        if self.invoice_date:
            hj = self.invoice_date
        else:
            hj = date.today()
        dia = hj.day
        mes = hj.month
        ano = hj.year
        if dia_preferencia:
            if dia >= dia_preferencia:
                mes = mes + 1
                if mes > 12:
                    mes = 1
                    ano = ano + 1            
            dia = dia_preferencia
        mes = mes + parcela

        if mes > 12 and mes < 25:
            mes = mes - 12
            ano = ano + 1
        if mes > 24 and mes < 37:
            mes = mes - 24
            ano = ano + 2
        if mes > 36 and mes < 49:
            mes = mes - 36
            ano = ano + 3
        if mes > 48 and mes < 61:
            mes = mes - 48
            ano = ano + 4
        if mes > 60 and mes < 73:
            mes = mes - 60
            ano = ano + 5
        if mes > 72 and mes < 85:
            mes = mes - 72
            ano = ano + 6
        if mes > 84 and mes < 97:
            mes = mes - 84
            ano = ano + 7
        if mes > 96 and mes < 109:
            mes = mes - 96
            ano = ano + 8
        if mes > 108 and mes < 121:
            mes = mes - 108
            ano = ano + 9
        
        if dia > 28 and mes == 2:
            dia = 28
        if dia == 31 and mes not in (1,3,5,7,8,10,12):
            dia = 30
        data_str = '%s-%s-%s' %(ano, mes, dia)
        data_vcto = datetime.strptime(data_str,'%Y-%m-%d').date()
        return data_vcto

    @api.depends('num_parcela', 'dia_vcto', 'vlr_prim_prc')
    def action_calcula_parcela(self):
        import pudb;pu.db
        prcs = []       
        prc = 0
        # if self.rateio_frete:
        total = self.amount_total
        #else:
        #    total = self.amount_total - self.amount_freight_value
        valor_prc = 0.0
        if self.vlr_prim_prc:
            total = self.currency_id.round(total - self.vlr_prim_prc)
            if self.num_parcela > 1:
                valor_prc = self.currency_id.round(total / (self.num_parcela - 1))
            else:
                if self.num_parcela > 1:
                    valor_prc = self.currency_id.round(total / (self.num_parcela - 1))
                else:
                    valor_prc = self.currency_id.round(total)
        else:
            if self.num_parcela > 0:
                valor_prc = self.currency_id.round(total / self.num_parcela)
            else:
                valor_prc = self.currency_id.round(total)
        valor_parc = valor_prc
        while (prc < self.num_parcela):
            data_parc = self.calcular_vencimento(self.dia_vcto,prc)
            if prc == 0 and self.vlr_prim_prc > 0.0:
                valor_parc = self.currency_id.round(self.vlr_prim_prc)
            if prc == 0 and self.vlr_prim_prc == 0.0:
                total -= valor_parc
            elif prc > 0:
                total -= valor_parc
            if (self.num_parcela - prc) == 1:
                if total > 0.0 or total < 0.0:
                    valor_parc = self.currency_id.round(valor_parc + total)
            #if not self.rateio_frete and prc == 0:
            #    valor_parc = valor_parc + self.amount_freight_value
            prcs.append((0, None, {
                'currency_id': self.currency_id.id,
                'data_vencimento': data_parc,
                'valor': self.currency_id.round(valor_parc),
                'numero_fatura': str(prc+1).zfill(2),
                'payment_mode_id': self.payment_mode_id.id,
            }))
            valor_parc = valor_prc
            prc += 1
        if prcs:
            if self.parcela_ids:
                self.parcela_ids.unlink()
            self.parcela_ids = prcs
                
    # def _compute_payment_terms(self, date, total_balance, total_amount_currency):
    #     import pudb;pu.db
    #     pass

    def _recompute_payment_terms_lines(self):
        import pudb;pu.db
        self.ensure_one()
        self = self.with_company(self.company_id)
        in_draft_mode = self != self._origin
        today = fields.Date.context_today(self)
        self = self.with_company(self.journal_id.company_id)

        def _get_payment_terms_computation_date(self):
            ''' Get the date from invoice that will be used to compute the payment terms.
            :param self:    The current account.move record.
            :return:        A datetime.date object.
            '''
            if self.invoice_payment_term_id:
                return self.invoice_date or today
            else:
                return self.invoice_date_due or self.invoice_date or today

        def _get_payment_terms_account(self, payment_terms_lines):
            ''' Get the account from invoice that will be set as receivable / payable account.
            :param self:                    The current account.move record.
            :param payment_terms_lines:     The current payment terms lines.
            :return:                        An account.account record.
            '''
            if payment_terms_lines:
                # Retrieve account from previous payment terms lines in order to allow the user to set a custom one.
                return payment_terms_lines[0].account_id
            elif self.partner_id:
                # Retrieve account from partner.
                if self.is_sale_document(include_receipts=True):
                    return self.partner_id.property_account_receivable_id
                else:
                    return self.partner_id.property_account_payable_id
            else:
                # Search new account.
                domain = [
                    ('company_id', '=', self.company_id.id),
                    ('internal_type', '=', 'receivable' if self.move_type in ('out_invoice', 'out_refund', 'out_receipt') else 'payable'),
                    ('deprecated', '=', False),
                ]
                return self.env['account.account'].search(domain, limit=1)

        def _compute_payment_terms(self, date, total_balance, total_amount_currency):
            ''' Compute the payment terms.
            :param self:                    The current account.move record.
            :param date:                    The date computed by '_get_payment_terms_computation_date'.
            :param total_balance:           The invoice's total in company's currency.
            :param total_amount_currency:   The invoice's total in invoice's currency.
            :return:                        A list <to_pay_company_currency, to_pay_invoice_currency, due_date>.
            '''
            if self.invoice_payment_term_id:
                # import pudb;pu.db
                to_compute = self.invoice_payment_term_id.compute(total_balance, date_ref=date, currency=self.company_id.currency_id)
                if not self.parcela_ids and self.currency_id == self.company_id.currency_id:
                    # Single-currency.
                    return [(b[0], b[1], b[1]) for b in to_compute]
                else:
                    lista_parcelas = []
                    for prc in self.parcela_ids:
                        lista_parcelas.append((prc.data_vencimento, -(prc.valor), -(prc.valor)))
                        
                    # Multi-currencies.
                    # to_compute_currency = self.invoice_payment_term_id.compute(total_amount_currency, date_ref=date, currency=self.currency_id)
                    # return [(b[0], b[1], ac[1]) for b, ac in zip(to_compute, to_compute_currency)]
                    return lista_parcelas    
            else:
                return [(fields.Date.to_string(date), total_balance, total_amount_currency)]

        """ Creates invoice related analytics and financial move lines """
        # account_move = self.env['account.move']
        
        def _compute_diff_payment_terms_lines(self, existing_terms_lines, account, to_compute):
            ''' Process the result of the '_compute_payment_terms' method and creates/updates corresponding invoice lines.
            :param self:                    The current account.move record.
            :param existing_terms_lines:    The current payment terms lines.
            :param account:                 The account.account record returned by '_get_payment_terms_account'.
            :param to_compute:              The list returned by '_compute_payment_terms'.
            '''
            # As we try to update existing lines, sort them by due date.
            existing_terms_lines = existing_terms_lines.sorted(lambda line: line.date_maturity or today)
            existing_terms_lines_index = 0

            # Recompute amls: update existing line or create new one for each payment term.
            new_terms_lines = self.env['account.move.line']
            for date_maturity, balance, amount_currency in to_compute:        
                currency = self.journal_id.company_id.currency_id
                if currency and currency.is_zero(balance) and len(to_compute) > 1:
                    continue
                
                if existing_terms_lines_index < len(existing_terms_lines):
                    # Update existing line.
                    candidate = existing_terms_lines[existing_terms_lines_index]
                    existing_terms_lines_index += 1
                    candidate.update({
                        'date_maturity': date_maturity,
                        'amount_currency': -amount_currency,
                        'debit': balance < 0.0 and -balance or 0.0,
                        'credit': balance > 0.0 and balance or 0.0,
                    })
                else:
                    # Create new line.
                    create_method = in_draft_mode and self.env['account.move.line'].new or self.env['account.move.line'].create
                    candidate = create_method({
                        'name': self.payment_reference or '',
                        'debit': balance < 0.0 and -balance or 0.0,
                        'credit': balance > 0.0 and balance or 0.0,
                        'quantity': 1.0,
                        'amount_currency': -amount_currency,
                        'date_maturity': date_maturity,
                        'move_id': self.id,
                        'currency_id': self.currency_id.id,
                        'account_id': account.id,
                        'partner_id': self.commercial_partner_id.id,
                        'exclude_from_invoice_tab': True,
                    })
                new_terms_lines += candidate
                if in_draft_mode:
                    candidate.update(candidate._get_fields_onchange_balance(force_computation=True))
            return new_terms_lines
        
        existing_terms_lines = self.line_ids.filtered(lambda line: line.account_id.user_type_id.type in ('receivable', 'payable'))
        others_lines = self.line_ids.filtered(lambda line: line.account_id.user_type_id.type not in ('receivable', 'payable'))
        company_currency_id = (self.company_id or self.env.company).currency_id
        total_balance = sum(others_lines.mapped(lambda l: company_currency_id.round(l.balance)))
        total_amount_currency = sum(others_lines.mapped('amount_currency'))

        if not others_lines:
            self.line_ids -= existing_terms_lines
            return

        computation_date = _get_payment_terms_computation_date(self)
        account = _get_payment_terms_account(self, existing_terms_lines)
        to_compute = _compute_payment_terms(self, computation_date, total_balance, total_amount_currency)
        import pudb;pu.db
        new_terms_lines = _compute_diff_payment_terms_lines(self, existing_terms_lines, account, to_compute)

        # Remove old terms lines that are no longer needed.
        self.line_ids -= existing_terms_lines - new_terms_lines

        if new_terms_lines:
            self.payment_reference = new_terms_lines[-1].name or ''
            self.invoice_date_due = new_terms_lines[-1].date_maturity


        # for inv in self:
        #     # if not inv.journal_id.sequence_id:
        #     #     raise UserError(_('Please define sequence on the journal related to this invoice.'))
        #     if not inv.invoice_line_ids:
        #         raise UserError(_('Please create some invoice lines.'))

        #     ctx = dict(self._context, lang=inv.partner_id.lang)

        #     if not inv.invoice_date:
        #         inv.with_context(ctx).write({'invoice_date': fields.Date.context_today(self)})
        #     date_due = inv.invoice_date
        #     if inv.parcela_ids:
        #         for prc in inv.parcela_ids:
        #              date_due= prc.data_vencimento
        #              break
        #     if not inv.date_due:
        #         inv.with_context(ctx).write({'date_due': date_due})
        #     company_currency = inv.company_id.currency_id

        #     # create move lines (one per invoice line + eventual taxes and analytic lines)
        #     iml = inv.invoice_line_move_line_get()
        #     iml += inv.tax_line_move_line_get()

        #     diff_currency = inv.currency_id != company_currency
        #     # create one move line for the total and possibly adjust the other lines amount
        #     total, total_currency, iml = inv.with_context(ctx).compute_invoice_totals(company_currency, iml)

        #     name = inv.name or '/'

        #     if inv.parcela_ids:
        #         for prc in inv.parcela_ids:
        #             if total < 0:
        #                 prc.valor = prc.valor*(-1)
        #             iml.append({
        #                 'type': 'dest',
        #                 'name': name,
        #                 'price': prc.valor,
        #                 'account_id': inv.account_id.id,
        #                 'payment_mode_id': prc.payment_mode_id.id,
        #                 'date_maturity': prc.data_vencimento,
        #                 'amount_currency': prc.valor,
        #                 'currency_id': inv.currency_id.id,
        #                 'move_id': inv.id
        #             })
        #             prc.valor = prc.valor*(-1)
                    
        #     elif inv.payment_term_id:
        #         totlines = inv.with_context(ctx).payment_term_id.with_context(currency_id=company_currency.id).compute(total, inv.invoice_date)[0]
        #         res_amount_currency = total_currency
        #         ctx['date'] = inv.date or inv.invoice_date
        #         for i, t in enumerate(totlines):
        #             if inv.currency_id != company_currency:
        #                 amount_currency = company_currency.with_context(ctx).compute(t[1], inv.currency_id)
        #             else:
        #                 amount_currency = False

        #             # last line: add the diff
        #             res_amount_currency -= amount_currency or 0
        #             if i + 1 == len(totlines):
        #                 amount_currency += res_amount_currency

        #             iml.append({
        #                 'type': 'dest',
        #                 'name': name,
        #                 'price': t[1],
        #                 'account_id': inv.account_id.id,
        #                 'date_maturity': t[0],
        #                 'payment_mode_id': inv.payment_mode_id.id,
        #                 'amount_currency': diff_currency and amount_currency,
        #                 'currency_id': diff_currency and inv.currency_id.id,
        #                 'move_id': inv.id
        #             })
        #     else:
        #         iml.append({
        #             'type': 'dest',
        #             'name': name,
        #             'price': total,
        #             'account_id': inv.account_id.id,
        #             'date_maturity': inv.date_due,
        #             'amount_currency': diff_currency and total_currency,
        #             'currency_id': diff_currency and inv.currency_id.id,
        #             'move_id': inv.id
        #         })
        #     part = self.env['res.partner']._find_accounting_partner(inv.partner_id)
        #     line = [(0, 0, self.line_get_convert(l, part.id)) for l in iml]
        #     line = inv.group_lines(iml, line)

        #     journal = inv.journal_id.with_context(ctx)
        #     line = inv.finalize_invoice_move_lines(line)

        #     date = inv.date or inv.invoice_date
        #     move_vals = {
        #         'ref': inv.reference,
        #         'line_ids': line,
        #         'journal_id': journal.id,
        #         'date': date,
        #         'narration': inv.comment,
        #     }
        #     ctx['company_id'] = inv.company_id.id
        #     ctx['invoice'] = inv
        #     ctx_nolang = ctx.copy()
        #     ctx_nolang.pop('lang', None)
        #     move = account_move.with_context(ctx_nolang).create(move_vals)
        #     # Pass invoice in context in method post: used if you want to get the same
        #     # account move reference when creating the same invoice after a cancelled one:
        #     move.post()
        #     # make the invoice point to that move
        #     vals = {
        #         'move_id': move.id,
        #         'date': date,
        #         'move_name': move.name,
        #     }
        #     inv.with_context(ctx).write(vals)  
                                                                                                                                                              
    def finalize_invoice_move_lines(self, move_lines):
        import pudb;pu.db
        res = super(AccountMove, self).\
        finalize_invoice_move_lines(move_lines)
        parcela = 1
        for line in move_lines:
            if 'name' in line[2]:
                for inv in self:
                    if inv.parcela_ids:
                        pm = inv.parcela_ids[parcela-1].payment_mode_id.id
                        parc = str(parcela).zfill(2)
                        if line[2]['name'] == parc:
                            line[2]['payment_mode_id'] = pm
                            parcela += 1
        return res

class InvoiceParcela(models.Model):
    _name = 'invoice.parcela'
    _order = 'data_vencimento'

    move_id = fields.Many2one('account.move', string="Fatura")
    currency_id = fields.Many2one(
        'res.currency', related='move_id.currency_id',
        string="EDoc Currency", readonly=True)
    numero_fatura = fields.Char(string=u"Número Fatura", size=60)
    data_vencimento = fields.Date(string="Data Vencimento")
    valor = fields.Monetary(string="Valor Parcela")
    payment_mode_id = fields.Many2one(
       'account.payment.mode', string=u"Modo de pagamento")
