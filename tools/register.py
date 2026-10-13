# GPL License

import bpy
import typing

__bl_classes = []
__bl_ordered_classes = []


def _dummy_operator_poll_message_set(message, *args):
    """Operator.poll_message_set was added in Blender 3.0. We add this function to Operator subclasses when it's not
    present so that code that wants to use poll_message_set won't cause errors on older Blender versions"""
    pass


def register_wrap(cls):
    if issubclass(cls, bpy.types.Operator) and not hasattr(cls, "poll_message_set"):
        # poll_message_set was added in Blender 3.0. To be able to use it on 3.0+, without causing errors on older
        # Blender versions, we need to add a dummy function under the same attribute name to the class.
        cls.poll_message_set = _dummy_operator_poll_message_set
    if hasattr(cls, 'bl_rna'):
        __bl_classes.append(cls)
    cls = make_annotations(cls)
    return cls


def make_annotations(cls):
    bl_props = {k: v for k, v in cls.__dict__.items() if isinstance(v, bpy.props._PropertyDeferred)}
    if bl_props:
        if '__annotations__' not in cls.__dict__:
            setattr(cls, '__annotations__', {})
        annotations = cls.__dict__['__annotations__']
        for k, v in bl_props.items():
            annotations[k] = v
            delattr(cls, k)
    return cls


def order_classes():
    global __bl_ordered_classes
    # Preserve decorator/import order for classes without dependencies. A set
    # makes panel ordering depend on Python's process-specific object hashes.
    classes_to_register = list(dict.fromkeys(iter_classes_to_register()))
    own_classes = set(classes_to_register)
    panels_by_id = {
        getattr(cls, 'bl_idname', '') or cls.__name__: cls
        for cls in classes_to_register
        if issubclass(cls, bpy.types.Panel)
    }
    deps_dict = {}
    for cls in classes_to_register:
        dependencies = set(iter_own_register_deps(cls, own_classes))
        if issubclass(cls, bpy.types.Panel):
            parent = panels_by_id.get(getattr(cls, 'bl_parent_id', ''))
            if parent is not None:
                dependencies.add(parent)
        deps_dict[cls] = dependencies

    # Panel parent IDs are registration dependencies, just like PointerProperty
    # types. This also works with fully qualified bl_ext.* package names.
    __bl_ordered_classes = toposort(deps_dict)


def iter_classes_to_register():
    for cls in __bl_classes:
        yield cls


def iter_own_register_deps(cls, own_classes):
    yield from (dep for dep in iter_register_deps(cls) if dep in own_classes)


def iter_register_deps(cls):
    for value in typing.get_type_hints(cls, {}, {}).values():
        dependency = get_dependency_from_annotation(value)
        if dependency is not None:
            yield dependency


def get_dependency_from_annotation(value):
    if isinstance(value, bpy.props._PropertyDeferred):
        if value.function in (bpy.props.PointerProperty, bpy.props.CollectionProperty):
            return value.keywords.get('type')
    if isinstance(value, tuple) and len(value) == 2:
        if value[0] in (bpy.props.PointerProperty, bpy.props.CollectionProperty):
            return value[1]["type"]
    return None


# Find order to register to solve dependencies
#################################################

def toposort(deps_dict):
    sorted_list = []
    pending = {cls: set(deps) for cls, deps in deps_dict.items()}
    while pending:
        ready = [cls for cls, deps in pending.items() if not deps]
        if not ready:
            names = ', '.join(cls.__name__ for cls in pending)
            raise RuntimeError('Cyclic Cats registration dependencies: ' + names)
        sorted_list.extend(ready)
        for cls in ready:
            del pending[cls]
        for dependencies in pending.values():
            dependencies.difference_update(ready)
    return sorted_list
