import config_loader

def replace_version(old_version, new_version):
    file_path = '/config/config.ini'
    with open(file_path, 'r') as file:
        filedata = file.read()

    filedata = filedata.replace(old_version, new_version)

    with open(file_path, 'w') as file:
        file.write(filedata)

def update_config(CONFIG_VERSION):
    if CONFIG_VERSION == '0.0.0':
        newKeys = "\n[Luscious]\ngenre_ids = ''\nmax_pages = 5\ncookie_name = ''\ncookie_value = ''\n"
        path = '/config/config.ini'
        with open(path, "a") as file:
            file.write(newKeys)
        replace_version("version = 0.0.0", "version = 1.0.0")
        print('Config upgrade to 1.0.0')