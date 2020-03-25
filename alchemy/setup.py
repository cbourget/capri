from setuptools import setup


name = 'capri.alchemy'

install_requires = [
    'SQLAlchemy'
]

setup(
    name=name,
    version='0.1.0',
    author='Charles-Éric Bourget',
    author_email='charlesericbourget@gmail.com',
    description='Capri alchemy',
    license='TBD',
    classifiers=[
        'Private :: Do Not Upload to pypi server'
    ],
    namespace_packages=['capri'],
    packages=[name],
    install_requires=install_requires
)
