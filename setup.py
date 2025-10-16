'''the setup.py file is essential part of packaging and distributing python project. It is used by setup
tools to define the configuration of the project such as its metadata , dependencies and all'''

from setuptools import find_packages , setup
from typing import List

def get_requirements()-> List[str]:
    '''
    this function will return list of requirements
    '''
    requirement_lst:List[str]=[]
    try:
        with open('requirements.txt') as file:
            #read lines from the file
            lines = file.readlines()
            #process each line
            for line in lines:
                requirement = line.strip()
                #ignore the empty lines and -e.
                
                if requirement and requirement!= '-e .':
                    requirement_lst.append(requirement)
    except  FileNotFoundError:
        print("requirements.txt not found")  
        
    return requirement_lst

setup(
    name="Network Security Project with Phishing Data",
    version="0.0.1",
    author="Prashant Shukla",
    author_email="prashantshukla9812@gmail.com",
    packages = find_packages(),
    install_requires = get_requirements()
    
)     
                
            

    
