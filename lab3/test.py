import main


def test_cli():
    import subprocess
    import os
    run_path = os.getcwd()
    os.chdir(os.path.join(os.path.dirname(__file__), 'test'))
    # noinspection PyBroadException
    try:
        subprocess.check_output(['test_cli.sh'])
        print('Test command line interface success')
    except Exception as e:
        print(e)
        print('Test command line interface failed')
    finally:
        os.chdir(run_path)


def test():
    test_data = [
        (  # Gap в начале
            ('AACGA', 'ACGA'),
            {
                ('AACGA', '_ACGA'),
                ('AACGA', 'A_CGA'),
            },
            2,
        ),
        (  # Gap в конце
            ('ACGAA', 'ACGA'),
            {
                ('ACGAA', 'ACGA_'),
                ('ACGAA', 'ACG_A'),
            },
            2,
        ),
        (  # Gap в середине
            ('AATCG', 'AACG'),
            {('AATCG', 'AA_CG')},
            2,
        ),
        (  # Несовпадение букв
            ('AABAA', 'AAAAA'),
            {('AABAA', 'AAAAA')},
            3,
        ),
        (  # Полное совпадение
            ('ABC', 'ABC'),
            {('ABC', 'ABC')},
            3,
        ),
        (  # Просто средний случайный пример
            ('BAACAABAAB', 'CBBCBAACBBABA'),
            {
                ('_BAACAA_BAAB_', 'CBBCBAACBBABA'),
                ('BAAC_AA_BAAB_', 'CBBCBAACBBABA'),
            },
            -4,
        ),
        (
            # Большой пример
            ('AACCBBCCDFGEEGGKKLQSDIVVMMQKKLRTNFCQCYKYWYQ', 'AABBCCDFGEEEGKKMPSTIVVMMQKMLRTNFCQCYKPWYQ'),
            {('AACCBBCCDFGEEGGKKLQSDIVVMMQKKLRTNFCQCYKYWYQ', 'AA__BBCCDFGEEEGKKMPSTIVVMMQKMLRTNFCQCYKPWYQ')},
            25,
        ),
        (  # Просто очень большой случайный пример
           # (Не проходит на сайте http://rna.informatik.uni-freiburg.de/Teaching/index.jsp?toolName=Needleman-Wunsch#
           # Но ответ верный. Score совпадает, при и цепочки при удалении _ совпадают с исходными
           # Два gap не встречается
            (
                'AAAYFEDTSNAHXCVPGFEFVDIXZSCMFLNMSGVTCSMAWLNISHWNRHPQMKXLTK'
                'RILRHEQAAIMIYQTWRVPQZMTFPYIRTZYYDYCDDERNGZYWNEHEBZBHFNDVME'
                'DXASESPKYKMQQXKQVZHDCXHQ',

                'EKLAPECVZFMLYGCKNBIBTCRXPMAZACKTRHMVEFNMQCWMCHMSBHCPYIHCGS'
                'CIPQIELPRBPTMMHQGRBGMFDKDSKBZSFGFGXAESPLTGGHFKMRQCDNTZQHIZ'
                'SSFMQREWYYMPGADLCNFNMCAEGAZWRYKLESMSMBXZDZNIDSGXXZLAEYLIVN',
            ),
            {
                (
                    '_AAAYFEDTSNAHXC__VPGFEFVDIXZSC____M_FLNMSGVTC__SMAWLNISHWN'
                    'RHPQ___MKXLT_KRILRHEQAAIMIYQTWRVPQZMTFP_YIRTZYYDYCD_DERNGZ'
                    '______YWNEHEBZBHFNDVM_EDXASESPK_YKM_QQXKQVZHD__CX_______HQ',

                    'EKLAPECVZFMLYGCKNBIBTCRXPMAZACKTRHMVEFNMQCWMCHMSBHCPYIHCGS'
                    'CIPQIELPRBPTMMHQGRBGMFDKDSKBZSFGFGXAESPLTGGHFKMRQCDNTZQHIZ'
                    'SSFMQREWYYMPGADLCNFNMCAEGAZWRYKLESMSMBXZDZNIDSGXXZLAEYLIVN',
                ),
                (
                    'A_AAYFEDTSNAHXC__VPGFEFVDIXZSC____M_FLNMSGVTC__SMAWLNISHWN'
                    'RHPQ___MKXLT_KRILRHEQAAIMIYQTWRVPQZMTFP_YIRTZYYDYCD_DERNGZ'
                    '______YWNEHEBZBHFNDVM_EDXASESPK_YKM_QQXKQVZHD__CX_______HQ',

                    'EKLAPECVZFMLYGCKNBIBTCRXPMAZACKTRHMVEFNMQCWMCHMSBHCPYIHCGS'
                    'CIPQIELPRBPTMMHQGRBGMFDKDSKBZSFGFGXAESPLTGGHFKMRQCDNTZQHIZ'
                    'SSFMQREWYYMPGADLCNFNMCAEGAZWRYKLESMSMBXZDZNIDSGXXZLAEYLIVN',
                ),
                (
                    'AA_AYFEDTSNAHXC__VPGFEFVDIXZSC____M_FLNMSGVTC__SMAWLNISHWN'
                    'RHPQ___MKXLT_KRILRHEQAAIMIYQTWRVPQZMTFP_YIRTZYYDYCD_DERNGZ'
                    '______YWNEHEBZBHFNDVM_EDXASESPK_YKM_QQXKQVZHD__CX_______HQ',

                    'EKLAPECVZFMLYGCKNBIBTCRXPMAZACKTRHMVEFNMQCWMCHMSBHCPYIHCGS'
                    'CIPQIELPRBPTMMHQGRBGMFDKDSKBZSFGFGXAESPLTGGHFKMRQCDNTZQHIZ'
                    'SSFMQREWYYMPGADLCNFNMCAEGAZWRYKLESMSMBXZDZNIDSGXXZLAEYLIVN',
                ),
                (
                    'AAAYFE_DTSNAHXC__VPGFEFVDIXZSC____M_FLNMSGVTC__SMAWLNISHWN'
                    'RHPQ___MKXLT_KRILRHEQAAIMIYQTWRVPQZMTFP_YIRTZYYDYCD_DERNGZ'
                    '______YWNEHEBZBHFNDVM_EDXASESPK_YKM_QQXKQVZHD__CX_______HQ',

                    'EKLAPECVZFMLYGCKNBIBTCRXPMAZACKTRHMVEFNMQCWMCHMSBHCPYIHCGS'
                    'CIPQIELPRBPTMMHQGRBGMFDKDSKBZSFGFGXAESPLTGGHFKMRQCDNTZQHIZ'
                    'SSFMQREWYYMPGADLCNFNMCAEGAZWRYKLESMSMBXZDZNIDSGXXZLAEYLIVN',
                ),
                (
                    'AAAYFED_TSNAHXC__VPGFEFVDIXZSC____M_FLNMSGVTC__SMAWLNISHWN'
                    'RHPQ___MKXLT_KRILRHEQAAIMIYQTWRVPQZMTFP_YIRTZYYDYCD_DERNGZ'
                    '______YWNEHEBZBHFNDVM_EDXASESPK_YKM_QQXKQVZHD__CX_______HQ',

                    'EKLAPECVZFMLYGCKNBIBTCRXPMAZACKTRHMVEFNMQCWMCHMSBHCPYIHCGS'
                    'CIPQIELPRBPTMMHQGRBGMFDKDSKBZSFGFGXAESPLTGGHFKMRQCDNTZQHIZ'
                    'SSFMQREWYYMPGADLCNFNMCAEGAZWRYKLESMSMBXZDZNIDSGXXZLAEYLIVN',
                ),
                (
                    'AAAYFEDT_SNAHXC__VPGFEFVDIXZSC____M_FLNMSGVTC__SMAWLNISHWN'
                    'RHPQ___MKXLT_KRILRHEQAAIMIYQTWRVPQZMTFP_YIRTZYYDYCD_DERNGZ'
                    '______YWNEHEBZBHFNDVM_EDXASESPK_YKM_QQXKQVZHD__CX_______HQ',

                    'EKLAPECVZFMLYGCKNBIBTCRXPMAZACKTRHMVEFNMQCWMCHMSBHCPYIHCGS'
                    'CIPQIELPRBPTMMHQGRBGMFDKDSKBZSFGFGXAESPLTGGHFKMRQCDNTZQHIZ'
                    'SSFMQREWYYMPGADLCNFNMCAEGAZWRYKLESMSMBXZDZNIDSGXXZLAEYLIVN',
                ),
                (
                    'AAAYFEDTS_NAHXC__VPGFEFVDIXZSC____M_FLNMSGVTC__SMAWLNISHWN'
                    'RHPQ___MKXLT_KRILRHEQAAIMIYQTWRVPQZMTFP_YIRTZYYDYCD_DERNGZ'
                    '______YWNEHEBZBHFNDVM_EDXASESPK_YKM_QQXKQVZHD__CX_______HQ',

                    'EKLAPECVZFMLYGCKNBIBTCRXPMAZACKTRHMVEFNMQCWMCHMSBHCPYIHCGS'
                    'CIPQIELPRBPTMMHQGRBGMFDKDSKBZSFGFGXAESPLTGGHFKMRQCDNTZQHIZ'
                    'SSFMQREWYYMPGADLCNFNMCAEGAZWRYKLESMSMBXZDZNIDSGXXZLAEYLIVN',
                ),
                (
                    'AAAYFEDTSN_AHXC__VPGFEFVDIXZSC____M_FLNMSGVTC__SMAWLNISHWN'
                    'RHPQ___MKXLT_KRILRHEQAAIMIYQTWRVPQZMTFP_YIRTZYYDYCD_DERNGZ'
                    '______YWNEHEBZBHFNDVM_EDXASESPK_YKM_QQXKQVZHD__CX_______HQ',

                    'EKLAPECVZFMLYGCKNBIBTCRXPMAZACKTRHMVEFNMQCWMCHMSBHCPYIHCGS'
                    'CIPQIELPRBPTMMHQGRBGMFDKDSKBZSFGFGXAESPLTGGHFKMRQCDNTZQHIZ'
                    'SSFMQREWYYMPGADLCNFNMCAEGAZWRYKLESMSMBXZDZNIDSGXXZLAEYLIVN',
                ),
                (
                    'AAAYFEDTSNA_HXC__VPGFEFVDIXZSC____M_FLNMSGVTC__SMAWLNISHWN'
                    'RHPQ___MKXLT_KRILRHEQAAIMIYQTWRVPQZMTFP_YIRTZYYDYCD_DERNGZ'
                    '______YWNEHEBZBHFNDVM_EDXASESPK_YKM_QQXKQVZHD__CX_______HQ',

                    'EKLAPECVZFMLYGCKNBIBTCRXPMAZACKTRHMVEFNMQCWMCHMSBHCPYIHCGS'
                    'CIPQIELPRBPTMMHQGRBGMFDKDSKBZSFGFGXAESPLTGGHFKMRQCDNTZQHIZ'
                    'SSFMQREWYYMPGADLCNFNMCAEGAZWRYKLESMSMBXZDZNIDSGXXZLAEYLIVN',
                ),
                (
                    'AAAYFEDTSNAH_XC__VPGFEFVDIXZSC____M_FLNMSGVTC__SMAWLNISHWN'
                    'RHPQ___MKXLT_KRILRHEQAAIMIYQTWRVPQZMTFP_YIRTZYYDYCD_DERNGZ'
                    '______YWNEHEBZBHFNDVM_EDXASESPK_YKM_QQXKQVZHD__CX_______HQ',

                    'EKLAPECVZFMLYGCKNBIBTCRXPMAZACKTRHMVEFNMQCWMCHMSBHCPYIHCGS'
                    'CIPQIELPRBPTMMHQGRBGMFDKDSKBZSFGFGXAESPLTGGHFKMRQCDNTZQHIZ'
                    'SSFMQREWYYMPGADLCNFNMCAEGAZWRYKLESMSMBXZDZNIDSGXXZLAEYLIVN',
                )
            },
            -154,
        )
    ][:-1]
    q = True
    for i, ((a, b), out, score) in enumerate(test_data):
        s, new_a, new_b = main.Hirscheberg(main.default_metric, main.D_GAP, a, b).out()
        check = 2 * ((new_a, new_b) not in out) + (s != score)
        if check == 3:
            q = False
            print('В тесте {} неправильный score и неверные цепочки'.format(i))
            print('Score: {} != {}'.format(score, s))
            print()
        elif check == 2:
            q = False
            print('В тесте {} неверные цепочки'.format(i))
            print(a)
            print(b)
            print(new_a)
            print(new_b)
        elif check == 1:
            q = False
            print('В тесте {} неправильный score'.format(i))
            print('Score: {} != {}'.format(score, s))
            print()
    if q:
        print('Test data success')


if __name__ == '__main__':
    test_cli()
    test()
