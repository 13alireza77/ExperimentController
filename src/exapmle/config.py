def generate_users(version, n=100000):
    np.random.seed(version)  # Seed for reproducibility
    phone_numbers = np.random.randint(1e7, 1e10, size=n)
    genders = np.random.choice(['girl', 'boy'], size=n)

    if version == 1:
        ages = np.random.normal(30, 10, n).astype(int)
        students = np.random.choice([True, False], size=n, p=[0.2, 0.8])
    elif version == 2:
        ages = np.random.normal(40, 15, n).astype(int)
        students = np.random.choice([True, False], size=n, p=[0.3, 0.7])
    else:
        ages = np.random.normal(25, 7, n).astype(int)
        students = np.random.choice([True, False], size=n, p=[0.6, 0.4])

    return pd.DataFrame({
        'phone_number': phone_numbers,
        'gender': genders,
        'age': ages,
        'is_student': students
    })


def generate_packages(version, n=100000):
    np.random.seed(version)  # Seed for reproducibility
    prices = np.random.randint(5, 50, size=n)
    periods = np.random.choice([30, 60, 120], size=n)
    types = np.random.choice(['regular', 'roaming'], size=n)
    sizes = np.random.choice([250, 750, 2000], size=n)

    if version == 1:
        sizes = np.random.choice([500, 1000, 1500], size=n)
    elif version == 2:
        sizes = np.random.choice([300, 600, 1200], size=n)
    else:
        sizes = np.random.choice([250, 750, 2000], size=n)

    return pd.DataFrame({
        'price': prices,
        'period': periods,
        'type': types,
        'size': sizes
    })


def generate_sales(users, packages, version, n=100000):
    np.random.seed(version)  # Seed for reproducibility
    # Assume each user makes between 1 and 3 purchases
    num_purchases = np.random.randint(1, 4, size=n)
    phone_numbers = np.random.choice(users['phone_number'], size=n)
    package_ids = np.random.choice(packages.index, size=n)

    sales_data = pd.DataFrame({
        'phone_number': np.repeat(phone_numbers, num_purchases),
        'package_id': np.random.choice(packages.index, size=n)
    })

    return sales_data


import numpy as np
import pandas as pd


class MockDataGenerator:
    _users_size = 10
    _packages_size = 1000
    _sales_size = 100

    def __init__(self, version):
        self.version = version
        self.users = self.generate_users()
        self.packages = self.generate_packages()
        self.sales = self.generate_sales()

    def generate_users(self):
        np.random.seed(self.version)  # Seed for reproducibility
        phone_numbers = np.random.randint(1e7, 1e10, size=self._users_size)
        genders = np.random.choice(['girl', 'boy'], size=self._users_size)

        if self.version == 1:
            ages = np.random.normal(30, 10, self._users_size).astype(int)
            students = np.random.choice([True, False], size=self._users_size, p=[0.2, 0.8])
        elif self.version == 2:
            ages = np.random.normal(40, 15, self._users_size).astype(int)
            students = np.random.choice([True, False], size=self._users_size, p=[0.3, 0.7])
        else:
            ages = np.random.normal(25, 7, self._users_size).astype(int)
            students = np.random.choice([True, False], size=self._users_size, p=[0.6, 0.4])

        return pd.DataFrame({
            'phone_number': phone_numbers,
            'gender': genders,
            'age': ages,
            'is_student': students
        })

    def generate_packages(self):
        np.random.seed(self.version)  # Seed for reproducibility
        prices = np.random.randint(5, 50, size=self._packages_size)
        periods = np.random.choice([30, 60, 120], size=self._packages_size)
        types = np.random.choice(['regular', 'roaming'], size=self._packages_size)

        if self.version == 1:
            sizes = np.random.choice([500, 1000, 1500], size=self._packages_size)
        elif self.version == 2:
            sizes = np.random.choice([300, 600, 1200], size=self._packages_size)
        else:
            sizes = np.random.choice([250, 750, 2000], size=self._packages_size)

        return pd.DataFrame({
            'price': prices,
            'period': periods,
            'type': types,
            'size': sizes
        })

    def generate_sales(self):
        num_purchases = np.random.randint(1, 4, size=self._sales_size)
        phone_numbers = np.random.choice(self.users['phone_number'], size=self._sales_size)
        package_ids = np.random.choice(self.packages.index, size=self._sales_size)

        sales_data = pd.DataFrame({
            'phone_number': np.repeat(phone_numbers, num_purchases),
            'package_id': np.repeat(package_ids, num_purchases)
        })

        return sales_data

    def get_users(self):
        return self.users

    def get_packages(self):
        return self.packages

    def get_sales(self):
        return self.sales


mock_data_generator = MockDataGenerator(version=1)
