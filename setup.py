from setuptools import setup, find_packages
setup(
    name='edgegrid-python', 
    version='1.1.1', 
    description='{OPEN} client authentication protocol for python-requests',
    author='Jonathan Landis',
    author_email='jlandis@akamai.com',
    url='https://github.com/akamai-open/AkamaiOPEN-edgegrid-python',
    namespace_packages=['akamai'],
    packages=find_packages(),
    python_requires=">=2.7.10",
    install_requires = [
        'requests>=2.3.0',
        'pyOpenSSL >= 0.13',
        'ndg-httpsclient',
        'pyasn1',
        'urllib3'
    ],
    license='LICENSE.txt'
)
