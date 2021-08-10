from setuptools import setup, find_packages
setup(
    name='edgegrid-python', 
    version='1.2.0', 
    description='{OPEN} client authentication protocol for python-requests',
    author='Jonathan Landis',
    author_email='jlandis@akamai.com',
    maintainer='Akamai Developer Experience team',
    maintainer_email='dl-devexp-eng@akamai.com',
    url='https://github.com/akamai/AkamaiOPEN-edgegrid-python',
    namespace_packages=['akamai'],
    packages=find_packages(),
    python_requires=">=2.7.10",
    install_requires=[
        'requests>=2.3.0',
        'pyOpenSSL>=19.0.0',
        'ndg-httpsclient',
        'pyasn1',
        'urllib3'
    ],
    license='Apache 2.0',
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
    ]
)
