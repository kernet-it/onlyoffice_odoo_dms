# Copyright (C) 2026 Data Dance s.r.o., Ascensio System SIA
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0-standalone.html).

import base64

from odoo.tests import TransactionCase, tagged

from odoo.addons.onlyoffice_odoo_dms.models.onlyoffice_dms_access import (
    _ROLES_ALL,
    _ROLES_READONLY,
    _filter_roles_by_file,
)


@tagged("post_install", "-at_install")
class TestFilterRolesByFile(TransactionCase):
    """Unit tests for the _filter_roles_by_file helper (pure logic, no DB)."""

    def test_no_file_name_returns_roles_unchanged(self):
        result = _filter_roles_by_file(_ROLES_ALL, None)
        self.assertEqual(result, _ROLES_ALL)

    def test_empty_file_name_returns_roles_unchanged(self):
        result = _filter_roles_by_file(_ROLES_ALL, "")
        self.assertEqual(result, _ROLES_ALL)

    def test_roles_readonly_is_subset_of_roles_all(self):
        all_keys = {key for key, _ in _ROLES_ALL}
        for key, _ in _ROLES_READONLY:
            self.assertIn(key, all_keys, msg=f"Role '{key}' in _ROLES_READONLY not found in _ROLES_ALL")

    def test_none_role_present_in_all_lists(self):
        all_keys = {key for key, _ in _ROLES_ALL}
        readonly_keys = {key for key, _ in _ROLES_READONLY}
        self.assertIn("none", all_keys)
        self.assertIn("none", readonly_keys)

    def test_edit_role_in_roles_all(self):
        all_keys = {key for key, _ in _ROLES_ALL}
        self.assertIn("edit", all_keys)

    def test_edit_role_not_in_roles_readonly(self):
        readonly_keys = {key for key, _ in _ROLES_READONLY}
        self.assertNotIn("edit", readonly_keys)

    def test_roles_all_not_empty(self):
        self.assertTrue(len(_ROLES_ALL) > 0)

    def test_roles_all_are_tuples_of_two_strings(self):
        for item in _ROLES_ALL:
            self.assertIsInstance(item, tuple)
            self.assertEqual(len(item), 2)
            self.assertIsInstance(item[0], str)
            self.assertIsInstance(item[1], str)


@tagged("post_install", "-at_install")
class TestOnlyofficeDmsFileAccessUser(TransactionCase):
    """Integration tests for the onlyoffice.dms.file.access.user model."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.storage = cls.env["dms.storage"].create(
            {
                "name": "Test OO Storage",
                "save_type": "database",
            }
        )
        cls.directory = cls.env["dms.directory"].create(
            {
                "name": "Test OO Directory",
                "is_root_directory": True,
                "storage_id": cls.storage.id,
            }
        )
        cls.dms_file = cls.env["dms.file"].create(
            {
                "name": "test_document.docx",
                "directory_id": cls.directory.id,
                "content": base64.b64encode(b"PK\x03\x04"),
            }
        )

    def test_create_user_access_record_view_role(self):
        access = self.env["onlyoffice.dms.file.access.user"].create(
            {
                "file_id": self.dms_file.id,
                "user_id": self.env.user.id,
                "role": "view",
            }
        )
        self.assertEqual(access.role, "view")
        self.assertEqual(access.file_id, self.dms_file)
        self.assertEqual(access.user_id, self.env.user)

    def test_create_user_access_record_edit_role(self):
        user2 = self.env["res.users"].create({"name": "OO Editor", "login": "oo_editor"})
        access = self.env["onlyoffice.dms.file.access.user"].create(
            {
                "file_id": self.dms_file.id,
                "user_id": user2.id,
                "role": "edit",
            }
        )
        self.assertEqual(access.role, "edit")

    def test_unique_user_file_constraint_raises(self):
        file2 = self.env["dms.file"].create(
            {
                "name": "unique_test.docx",
                "directory_id": self.directory.id,
                "content": base64.b64encode(b"PK\x03\x04"),
            }
        )
        self.env["onlyoffice.dms.file.access.user"].create(
            {
                "file_id": file2.id,
                "user_id": self.env.user.id,
                "role": "view",
            }
        )
        with self.assertRaises(Exception):  # noqa: B017
            self.env["onlyoffice.dms.file.access.user"].create(
                {
                    "file_id": file2.id,
                    "user_id": self.env.user.id,
                    "role": "edit",
                }
            )

    def test_oo_is_viewable_for_docx(self):
        self.assertTrue(self.dms_file.oo_is_viewable)

    def test_oo_is_editable_for_docx(self):
        self.assertTrue(self.dms_file.oo_is_editable)

    def test_oo_is_not_editable_for_unknown_ext(self):
        unknown_file = self.env["dms.file"].create(
            {
                "name": "archive.xyz_not_supported",
                "directory_id": self.directory.id,
                "content": base64.b64encode(b"data"),
            }
        )
        self.assertFalse(unknown_file.oo_is_editable)

    def test_directory_link_access_default_none(self):
        self.assertEqual(self.directory.oo_link_access, "none")

    def test_directory_link_access_set(self):
        self.directory.oo_link_access = "view"
        self.assertEqual(self.directory.oo_link_access, "view")

    def test_get_oo_effective_link_access_inherits_from_parent(self):
        sub_dir = self.env["dms.directory"].create(
            {
                "name": "Sub OO Directory",
                "parent_id": self.directory.id,
            }
        )
        self.directory.oo_link_access = "commenter"
        effective = sub_dir._get_oo_effective_link_access()
        self.assertEqual(effective, "commenter")

    def test_get_oo_effective_link_access_child_overrides_parent(self):
        sub_dir = self.env["dms.directory"].create(
            {
                "name": "Sub OO Dir Override",
                "parent_id": self.directory.id,
            }
        )
        self.directory.oo_link_access = "view"
        sub_dir.oo_link_access = "edit"
        effective = sub_dir._get_oo_effective_link_access()
        self.assertEqual(effective, "edit")
