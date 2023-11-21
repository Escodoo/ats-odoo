{
    'name': 'Desconto Total na Venda',
    'description': 'Permite adicionar um desconto em Valor no total geral',
    'version': '14.0.1.0.0',
    'license': 'LGPL-3',
    'category': 'Sales',
    'author': 'ATSTi',
    'website': '',
    'depends': [
        'l10n_br_sale',  
    ],
    'data': [
        'views/sale_order_view.xml',
        # 'views/account_invoice_view.xml',
    ],
    'application': False,
    'installable': True,
}
