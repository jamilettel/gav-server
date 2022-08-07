def get_ind_enc_indexes():
    return {
        'encoding_type': 'indexes'
    }

def get_ind_enc_range(minimum: int | float, maximum: int | float):
    return {
        'encoding_type': 'range',
        'range': [minimum, maximum]
    }

def get_ind_enc_boolean():
    return {
        'encoding_type': 'boolean',
    }