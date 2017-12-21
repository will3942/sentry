from __future__ import absolute_import

from sentry.testutils import PermissionTestCase, TestCase
from django.core.urlresolvers import reverse
from sentry.models import TotpInterface


class OrganizationIndexPermissionTest(PermissionTestCase):
    def setUp(self):
        super(OrganizationIndexPermissionTest, self).setUp()
        self.org_owner = self.create_user()
        self.org_user = self.create_user()
        self.org = self.create_organization(owner=self.org_owner)

        TotpInterface().enroll(self.org_owner)
        self.login_as(self.org_owner)
        self.client.put(reverse('sentry-api-0-organization-details', kwargs={
            'organization_slug': self.org.slug,
        }))

        self.org_member = self.create_member(user=self.org_user, organization=self.org)
        self.org_index_path = reverse(
            'sentry-organization-home', args=[self.org.slug]
        )
        self.sentry_index_path = reverse('sentry')
        self.login_as(self.org_user)


class OrganizationMemberSettingsTest(TestCase):
    def test_hello(self):
        pass
