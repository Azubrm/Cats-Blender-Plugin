# Blender 5.2 compatibility notes

Target: Blender 5.2.2 LTS, as listed on the [official download page](https://www.blender.org/download/)
on 2026-10-13. Package version: 5.2.2. The manifest accepts Blender 5.0 through
5.2 and stops before 5.3, which is outside this adaptation's scope.

## Validation status

At the requester's direction, Blender was not launched and no tests, compiler
checks, extension validation, installation checks, or functional smoke tests
were run as part of this adaptation. Changes are based on source inspection,
bundled Blender 5.2 Python source, and official API documentation. The user
reports that 5.2.1 enables without errors after restarting Blender, but shows
extension namespace warnings. The 5.2.2 changes have not been runtime tested;
full functional compatibility remains unverified.

## 5.2.2 extension namespace fix

Blender reported `Policy violation with top level module: mmd_tools_local...`
and `Policy violation with sys.path: .\\extern_tools`. Cats previously appended
its bundled dependencies directory to the global Python search path and
imported MMD Tools as a top-level package.

Version 5.2.2 uses relative imports under the extension package for MMD Tools
and its bundled OpenCC entry point, removes the search-path modification, and
uses the full package name for property processing and preference lookup.
Optional bundled Immersive Scaler lookup also uses a qualified package name;
separately installed add-ons continue to be discovered through Blender.
Operator IDs and persistent RNA property names are unchanged.

Save your work and fully restart Blender after updating from an earlier
version. Reinstalling inside the same process can retain the old top-level
modules and their warnings until Blender exits.

## 5.2.1 registration fix

A user installation of 5.2.0 reported that `VIEW3D_PT_eye_tracking_v3` was
missing when registering `VIEW3D_PT_eye_tracking_legacy_v3`. The registration
sorter used an unordered set and did not include `bl_parent_id` dependencies.
Version 5.2.1 preserves declaration order for unrelated classes, registers
parents before sub-panels, and reports dependency cycles instead of hanging.
This also covers the custom-model and optimization panel hierarchies. The user
subsequently reported successful enabling after a full Blender restart.

## Installation and updates

This package uses the native extension manifest, including permission reasons
and bundled wheels. Requests and its dependencies are pure Python wheels usable
with both Python 3.11 and 3.13. Exact pins are in `wheels/requirements.txt`.
The wheels are the original PyPI distributions, including their license files.

The built-in legacy updater is disabled. It targets archived upstream Blender
5.0 code and would replace this fork's compatibility work. Use Blender's
**Install from Disk** to install an updated fork ZIP instead.

The old installer-cleanup routine is no longer called during registration;
Blender's extension installer handles the extension's own directory. Older
legacy Cats copies must be disabled before enabling this fork to prevent class
and operator name collisions.

## Limitations

- Optional external add-ons and their compatibility are outside this patch.
- Blender removed its built-in Collada importer/exporter. Cats cannot restore
  that feature by changing Python calls; convert DAE files with an appropriate
  external tool or use a separately maintained importer.
- Online translation and dictionary downloads still depend on external services.
- This is not an extensions.blender.org submission; inherited network operations
  have not all been migrated to Blender's online-access setting.
- Blender 5.3 prereleases and later versions are not included in this target.
- Existing project files and installed Cats versions were not modified.

## API references

- [Blender 5.0 Python API changes](https://developer.blender.org/docs/release_notes/5.0/python_api/)
- [Blender 5.1 Python API changes](https://developer.blender.org/docs/release_notes/5.1/python_api/)
- [Blender compatibility notes](https://developer.blender.org/docs/release_notes/compatibility/)
- [Action slots](https://docs.blender.org/api/5.0/bpy.types.ActionSlots.html)
- [Blender 5.0 pipeline changes, including Collada removal](https://developer.blender.org/docs/release_notes/5.0/pipeline_io/)
- [Extension Python wheels](https://docs.blender.org/manual/en/latest/advanced/extensions/python_wheels.html)
- [Extension moderation guidelines](https://developer.blender.org/docs/features/extensions/moderation/guidelines/)
