import os, pathlib
mods = ['pms_base', 'pms_portal_resident', 'pms_community_center', 'sc_google_home']
base_path = pathlib.Path('./odoo19-shadow/addons')
for mod in mods:
    (base_path / mod).mkdir(parents=True, exist_ok=True)
    (base_path / mod / '__init__.py').write_text('')
    manifest = f"""{{
    'name': '{mod.replace("_", " ").title()}',
    'version': '19.0.2.0',
    'depends': ['base' if mod == 'pms_base' else 'pms_base'],
    'category': 'Property Management',
    'license': 'OEEL-1',
}}"""
    (base_path / mod / '__manifest__.py').write_text(manifest)
print("Core PMS directories prepared.")
