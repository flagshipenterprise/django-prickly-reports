def get_ids_from_getlist(getlist):
    try:
        return [int(_id) for _id in getlist]
    except:
        return []


def format_querystring_for_id_list(name, ids):
    return '?' + '&'.join(['%s=%s' % (name, _id) for _id in ids])


def get_remove_url_for_tag(tag, all_tag_ids):
    filtered_ids = [tag_id for tag_id in all_tag_ids if tag_id != tag.id]
    return format_querystring_for_id_list('tag', filtered_ids)


def get_filtered_loans_csv_data(loans, last_month, today):
    rows = []
    rows.append([
        'Client Name',
        'Original Loan Amount',
        'Balance after %s Payments' % last_month,
        '%s Loan Payments' % last_month,
        '%s Payments Interest' % last_month,
        '%s Payments Principal' % last_month,
        'Original Loan Date',
        'Loan Term in Months',
        'Interest',
        'Funding Source',
    ])
    for loan in loans:
        last_months_payments = loan.get_last_months_payments(today)
        rows.append([
            loan.client,
            loan.amount,
            '%.2f' % last_months_payments['balance'],
            '%.2f' % last_months_payments['payment'],
            '%.2f' % last_months_payments['interest'],
            '%.2f' % last_months_payments['principal'],
            loan.start_date,
            loan.term,
            loan.interest_rate,
            loan.funding_source,
        ])
    return rows


def get_filtered_ta_csv_data(ta_report):
    return [
        [
            '',
            'Filtered Actual Hours',
            'Filtered Budget Hours',
        ],
        [
            'Pre Loan',
            ta_report['pre']['actual'],
            ta_report['pre']['budgeted'],
        ],
        [
            'Post Loan',
            ta_report['post']['actual'],
            ta_report['post']['budgeted'],
        ],
        [
            'Admin',
            ta_report['admin']['actual'],
            ta_report['admin']['budgeted'],
        ],
        [
            'Total',
            ta_report['total']['actual'],
            ta_report['total']['budgeted'],
        ],
    ]


def get_filtered_cu_csv_data(ta_report):
    rows = []
    rows.append(['Month', 'Total Sales', 'Total Profit', 'Total Full Time Equivalent Employees'])
    for month in ta_report:
        rows.append([
            month['month'],
            month['total_sales'],
            month['total_profit'],
            month['total_ftes'],
        ])

    return rows
