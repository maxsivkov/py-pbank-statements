from setuptools import setup, find_packages

setup(name='py-pbank-statements',
      version='0.1',
      description='Bank Statements',
      url='https://github.com/maxsivkov/py-pbank-statements',
      author='Max Sivkov',
      author_email='maxsivkov@gmail.com',
      license='MIT',
      packages=find_packages(),
      install_requires=[
            'openpyxl',
            'pyyaml',
            'ujson',
            'isodate',
            'marshmallow-dataclass',
            'confuse',
            'requests',
            'pyexcel',
            'pyexcel-xls',
            'pyexcel-xlsx',
      ],
      zip_safe=False)