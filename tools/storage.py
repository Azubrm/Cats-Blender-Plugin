# GPL License

"""Writable extension data with read-only fallback to legacy resources."""

import os

import bpy


ADDON_PACKAGE = __package__.rsplit('.', 1)[0]
RESOURCES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resources')


def user_directory(*parts, create=False):
    if ADDON_PACKAGE.startswith('bl_ext.'):
        root = bpy.utils.extension_path_user(ADDON_PACKAGE, create=create)
    else:
        root = bpy.utils.user_resource('DATAFILES', path='cats', create=create)
    directory = os.path.join(root, *parts)
    if create:
        os.makedirs(directory, exist_ok=True)
    return directory


def user_file(*parts, create=False):
    return os.path.join(user_directory(*parts[:-1], create=create), parts[-1])


def readable_resource(*parts):
    """Prefer saved user data; keep existing installations readable."""
    path = user_file(*parts)
    if os.path.isfile(path):
        return path
    return os.path.join(RESOURCES_DIR, *parts)


def resource_files(directory):
    """List both bundled files and user overrides without duplicates."""
    names = set()
    for path in (os.path.join(RESOURCES_DIR, directory), user_directory(directory)):
        if os.path.isdir(path):
            names.update(name for name in os.listdir(path)
                         if os.path.isfile(os.path.join(path, name)))
    return sorted(names)
