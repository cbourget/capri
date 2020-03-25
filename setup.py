from setuptools import setup

package_name = 'capri'
version = '0.1.0'

install_requires = []

extras_require={
    'tests': [
        'coverage',
        'flake8',
        'pytest',
        'pytest-cov'
    ]
}

setup(
    name=package_name,
    version=version,
    author='Charles-Éric Bourget',
    author_email='charlesericbourget@gmail.com',
    description='Capri',
    license='TBD',
    classifiers=[
        'Private :: Do Not Upload to pypi server'
    ],
    install_requires=install_requires,
    extras_require=extras_require
)
