# Copyright (C) 2026 Data Dance s.r.o., Ascensio System SIA
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0-standalone.html).

import base64
import io
import json
import re
from unittest.mock import patch

from odoo.tests import HttpCase, new_test_user, tagged

from odoo.addons.onlyoffice_odoo.utils import config_constants, config_utils, jwt_utils

URLOPEN = "odoo.addons.onlyoffice_odoo_dms.controllers.controllers.onlyoffice_urlopen"
INTERNAL_SECRET = "test-internal-secret"


@tagged("post_install", "-at_install")
class TestDmsControllers(HttpCase):
    """The DMS routes on the editor page and the connector of onlyoffice_odoo."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        config_utils.set_jwt_secret(cls.env, "")
        # A preset secret: get_internal_jwt_secret otherwise generates one and commits the test transaction.
        cls.env["ir.config_parameter"].sudo().set_param(config_constants.INTERNAL_JWT_SECRET, INTERNAL_SECRET)
        cls.editor = new_test_user(cls.env, login="oo_dms_editor", groups="base.group_user,dms.group_dms_user")
        access_group = cls.env["dms.access.group"].create(
            {
                "name": "Test OO Editors",
                "perm_create": True,
                "perm_write": True,
                "oo_role": "edit",
                "explicit_user_ids": [(6, 0, cls.editor.ids)],
            }
        )
        storage = cls.env["dms.storage"].create({"name": "Test OO Storage", "save_type": "database"})
        directory = cls.env["dms.directory"].create(
            {
                "name": "Test OO Directory",
                "is_root_directory": True,
                "storage_id": storage.id,
                "group_ids": [(6, 0, access_group.ids)],
            }
        )
        cls.dms_file = cls.env["dms.file"].create(
            {
                "name": "test_document.docx",
                "directory_id": directory.id,
                "content": base64.b64encode(b"PK\x03\x04"),
            }
        )

    def test_editor_page_renders_the_dms_config(self):
        self.authenticate("oo_dms_editor", "oo_dms_editor")

        response = self.url_open(f"/onlyoffice/dms/editor/{self.dms_file.id}")

        self.assertEqual(response.status_code, 200)
        config = json.loads(re.search(r"var config = (.*);\n", response.text).group(1))
        self.assertEqual(config["document"]["title"], "test_document.docx")
        self.assertIn(f"onlyoffice/dms/file/content/{self.dms_file.id}?", config["document"]["url"])
        self.assertIn(f"onlyoffice/dms/editor/callback/{self.dms_file.id}?", config["editorConfig"]["callbackUrl"])
        self.assertEqual(config["editorConfig"]["mode"], "edit")
        self.assertRegex(response.text, r"odoo_custom_functions_init\.js\?v=\w+")

    def test_save_callback_writes_the_new_content(self):
        token = jwt_utils.encode_payload(self.env, {"id": self.editor.id}, INTERNAL_SECRET)
        body = {"status": 2, "url": "http://docserver/cache/files/new.docx"}

        with patch(URLOPEN, return_value=io.BytesIO(b"new content")) as urlopen:
            response = self.url_open(
                f"/onlyoffice/dms/editor/callback/{self.dms_file.id}?oo_security_token={token}",
                data=json.dumps(body),
                headers={"Content-Type": "application/json"},
            )

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json(), {"error": 0})
        urlopen.assert_called_once_with(body["url"])
        self.dms_file.invalidate_recordset()
        self.assertEqual(base64.b64decode(self.dms_file.content), b"new content")
        self.assertEqual(self.dms_file.oo_version, 1)
