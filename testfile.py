import yaml
import os

cwd = os.getcwd()

# Load settings
with open(cwd + '/src/settings.yaml', 'r') as settings_file:
    settings = yaml.load(settings_file, Loader=yaml.FullLoader)
    print(settings)

settings_file.close()