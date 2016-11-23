from tasks import check_registration

voter_data = {
        'first_name': 'Coleman',
        'last_name': 'Black',
        'birth_date': '1985-12-25',
        'postal_code': 'K1Z7X8',
        'street_number': '1456',
        'unit_number': '',
        }

voter_data = {
        'first_name': 'Ann',
        'last_name': 'Connolly',
        'birth_date': '1964-5-1',
        'postal_code': 'E2E2V2',
        'street_number': '118',
        'unit_number': '',
        }

task = check_registration.delay(voter_data)

task.get()

print(task.result)
