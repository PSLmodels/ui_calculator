from setuptools import setup

setup(name='ui_calculator',
      version='0.1.0',
      description='Unemployment insurance benefit calculator',
      url='http://github.com/ganong-noel/ui_calculator',
      author='Peter Ganong, Pascal Noel, Peter Robertson and Joseph Vavra',
      author_email='ganong@uchicago.edu',
      license='GPL',
      packages=['ui_calculator'],
      install_requires=[
          'numpy',
          'pandas'
      ],
      zip_safe=False
      # package_data={'ui_calculator': ['data/*']}
)
