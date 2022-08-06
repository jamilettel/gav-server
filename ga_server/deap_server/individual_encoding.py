def get_ind_enc_indexes():
    return {
        'encoding_type': 'indexes'
    }

def get_ind_enc_values(minimum: int | float, maximum: int | float):
    return {
        'encoding_type': 'values',
        'range': [minimum, maximum]
    }