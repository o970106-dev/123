{
    "name": "Resident Portal (PF Node)",
    "summary": "Glassmorphism UI and smart device control for residents",
    "version": "19.0.1.0",
    "category": "Property Management/Portal",
    "depends": ["pms_base", "portal"],
    "data": [
        "views/portal_templates.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "pms_portal_resident/static/src/css/portal.css",
            "pms_portal_resident/static/src/js/pms_telemetry.js",
        ],
    },
    "author": "Wuchang Life",
    "license": "OEEL-1",
}
