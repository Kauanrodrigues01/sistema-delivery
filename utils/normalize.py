def normalize_phone(phone):
    """Normaliza o número de telefone removendo caracteres especiais"""
    if phone:
        return phone.replace(".", "").replace("-", "").replace("(", "").replace(")", "").strip()
    return phone

def normalize_cpf(cpf):
    """Normaliza o CPF removendo pontos e traços"""
    if cpf:
        return cpf.replace(".", "").replace("-", "").strip()
    return cpf