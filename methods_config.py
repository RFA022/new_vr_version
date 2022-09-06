import ext_funs
def get_method_params(method_mame):
    if method_mame == 'm':
       params=[1,2,3,4]
    elif method_mame =='choose_position_m':
        pos_length=len(ext_funs.get_positions_fromCSV('Resources\RedAttackPos.csv'))
        params = []
        for i in range(pos_length):
            params.append(i)
    else:
       params=None
    return params