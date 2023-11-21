{
    'name': 'Desconto Total na Fatura',
    'description': 'Permite adicionar um desconto em Valor no total geral',
    'version': '14.0.1.0.0',
    'license': 'LGPL-3',
    'category': 'Accounting & Finance',
    'author': 'ATSTi',
    'website': '',
    'depends': [
        'l10n_br_account',  
    ],
    'data': [
        'views/account_move_view.xml',
        # 'views/account_invoice_view.xml',
    ],
    'application': False,
    'installable': True,
}
