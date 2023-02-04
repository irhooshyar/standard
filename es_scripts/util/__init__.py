from num2fawords import words, ordinal_words, HUNDREDS

HUNDREDS[1] = 'صد'
clause_type = {
    # search keyword: clause type
    'ماده': 'ماده',
    'تبصره': 'تبصره',
    'بند': 'بند',
    'جز': 'جزء',
}
clause_number_persian = {number: words(number) for number in range(1, 201)}
clause_number_number = {number: str(number) for number in range(1, 201)}
clause_number_nth = {number: ordinal_words(number) for number in range(1, 201)}
clause_number_alphabet = {
    1: 'الف',
    2: 'ب',
    3: 'ج',
    4: 'د',
    5: 'ه',
    6: 'و',
    7: 'ز',
    8: 'ح',
    9: 'ط',
    10: 'ی',
    11: 'ک',
    12: 'ل',
    13: 'م',
    14: 'ن',
    15: 'س',
    16: 'ع',
    17: 'ف',
    18: 'ص',
    19: 'ق',
    20: 'ر',
    21: 'ش',
    22: 'ت',
    23: 'ث',
    24: 'خ',
    25: 'ذ',
    26: 'ض',
    27: 'ظ',
    28: 'غ',
}
clause_number_arabic = {
    1: 'واحده',
    2: 'ثانی',
    3: 'ثالث',
}
clause_number_nth2 = {
    1: 'اول',
}
clause_number_all = [
    clause_number_alphabet,
    clause_number_number,
    clause_number_nth,
    clause_number_nth2,
    clause_number_arabic,
    clause_number_persian
]
clause_number_names = [
    'number_alphabet',
    'number_number',
    'number_nth',
    'number_nth',
    'number_arabic',
    'number_persian'
]

clause_number_dict = {
    'number_alphabet': clause_number_alphabet,
    'number_number': clause_number_number,
    'number_nth': clause_number_nth,
    'number_arabic': clause_number_arabic,
    'number_persian': clause_number_persian,
}

clause_number = {
    number: [num_dict[number] for num_dict in clause_number_all if number in num_dict.keys()] for number in
    range(1, max([max(item.keys()) for item in clause_number_all]))
}
