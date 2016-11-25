from tasks import check_registration

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
