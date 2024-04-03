import subprocess

# Get the output of `pip3 list`
pip_list_output = subprocess.run(['pip3', 'list'], capture_output=True, text=True).stdout

# Split the output into lines and skip the header
packages = pip_list_output.strip().split('\n')[2:]

# Extract package names from each line
package_names = [line.split()[0] for line in packages]

# Install each package using pip3
for package in package_names:
    subprocess.run(['pip3', 'install', '--upgrade', package])
