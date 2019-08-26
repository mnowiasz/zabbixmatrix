from setuptools import setup

setup(
    name='zabbixmatrix',
    version='0.0.2',
    packages=['zabbix2matrix'],
    url='https://github.com/mnowiasz/zabbixmatrix',
    license='MIT',
    author='Mark Nowiasz',
    author_email='buckaroo+zabbixmatrix@midworld.de',
    description='Send zabbix alerts to matrix',
    install_requires = ['matrix_client>=0.3.2'],
    entry_points = {
        'console_scripts': ['zabbix2matrix=zabbix2matrix.main:zabbix2matrixmain'],
    },
)
