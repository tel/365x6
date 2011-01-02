from setuptools import setup, find_packages
setup(
    name = '365x6',
    version = '0a',
    packages = ['app365'],

    install_requires = [e[0:-1] for e in open('deps.txt').readlines()],

    package_data = {
        'app365' : ['schema.sql', 'templates/*', 
                    'static/*.less', 'static/i/*', 'static/fancybox/*']
    }
)


