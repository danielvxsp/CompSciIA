from setuptools import setup, find_packages

setup(
    name="your_project_name",  # Replace with your project name
    version="0.1.0",  # Initial version of your project
    description="A short description of your project",
    packages=find_packages(),  # Automatically find and include all packages in your project
    install_requires=[
        'librosa',  # Add librosa as a required dependency
        'numpy',    # librosa requires numpy, so it's good practice to list it explicitly
        'scipy',    # librosa also depends on scipy
        # You can add more dependencies here if needed
    ],
)