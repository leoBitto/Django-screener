

def reclassification_balancesheet(bs):
    reclassified_bs = {
        'Assets':{
            'active circulation':{
                'immediate liquidity':0,
                'inventory':bs['Inventory'],
                'non immediate liquidity':0,
            },
            'Fixed Assets':{
                'Tangible':0,
                'Intangible':0,
                'Financial':0,
            }
        },
        'Liabilities':{
            'capital from others':{
                'current liabilities':bs['CurrentLiabilities'],
                'consolidated liabilities':0,
            },
            'net capital':{
                'social capital':0,
                'reserves':0,
                'profit/loss':0,
            }
        },
    }










    return reclassified_bs