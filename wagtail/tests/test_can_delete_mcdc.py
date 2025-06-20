from django.contrib.auth.models import Group, Permission, User
from django.test import TestCase

from wagtail.models import GroupPagePermission, Page
from wagtail.test.utils import WagtailTestUtils

class TestCanDeleteMCDC(WagtailTestUtils, TestCase):
    def setUp(self):
        # Utilizadores
        self.editor = self.create_user(username="editor", password="password")
        self.publisher = self.create_user(username="publisher", password="password")
        
        # Grupos de permissões
        self.editors_group = Group.objects.create(name="Editors")
        self.publishers_group = Group.objects.create(name="Publishers")

        # Permissões
        self.add_perm = Permission.objects.get(codename="add_page")
        self.bulk_delete_perm = Permission.objects.get(codename="bulk_delete_page")
        self.publish_perm = Permission.objects.get(codename="publish_page")
        
        # Atribuir permissões aos grupos
        self.editors_group.permissions.add(self.add_perm)
        self.publishers_group.permissions.add(self.add_perm, self.bulk_delete_perm, self.publish_perm)

        self.editor.groups.add(self.editors_group)
        self.publisher.groups.add(self.publishers_group)

        # Páginas
        self.root_page = Page.objects.get(pk=1)
        self.non_leaf_page = self.root_page.add_child(instance=Page(title="Página Não-Folha"))
        self.leaf_page = self.non_leaf_page.add_child(instance=Page(title="Página Folha"))

        # Atribuir permissões de grupo à raiz
        GroupPagePermission.objects.create(group=self.editors_group, page=self.root_page, permission=self.add_perm)
        GroupPagePermission.objects.create(group=self.publishers_group, page=self.root_page, permission=self.add_perm)
        GroupPagePermission.objects.create(group=self.publishers_group, page=self.root_page, permission=self.bulk_delete_perm)

    def test_can_delete_with_bulk_permission(self):
        # Ref: CT1
        permissions = self.non_leaf_page.permissions_for_user(self.publisher)
        self.assertTrue(permissions.can_delete())

    def test_can_delete_leaf_page_without_bulk_permission(self):
        # Ref: CT2
        permissions = self.leaf_page.permissions_for_user(self.editor)
        self.assertTrue(permissions.can_delete())

    def test_can_delete_non_leaf_when_ignoring_bulk(self):
        # Ref: CT3
        permissions = self.non_leaf_page.permissions_for_user(self.editor)
        self.assertTrue(permissions.can_delete(ignore_bulk=True))

    def test_cannot_delete_non_leaf_without_bulk_permission(self):
        # Ref: CT4
        permissions = self.non_leaf_page.permissions_for_user(self.editor)
        self.assertFalse(permissions.can_delete())
