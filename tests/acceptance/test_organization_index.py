from __future__ import absolute_import

from sentry.testutils import AcceptanceTestCase
from django.core.urlresolvers import reverse
from sentry.models import TotpInterface


class OrganizationIndexTest(AcceptanceTestCase):
    def setUp(self):
        super(OrganizationIndexTest, self).setUp()
        self.org_owner = self.create_user()
        self.org_user = self.create_user()
        self.org = self.create_organization(owner=None)
        import pdb
        pdb.set_trace()
        self.team = self.create_team(organization=self.org, name='Mariachi Band')
        self.create_member(
            user=self.org_owner,
            organization=self.org,
            role='owner',
            teams=[self.team],
        )
        TotpInterface().enroll(self.org_owner)
        self.login_as(self.org_owner)
        url = reverse('sentry-api-0-organization-details', kwargs={
            'organization_slug': self.org.slug,
        })
        response = self.client.put(url, data={
            'require2FA': True,
        })

        assert response.status_code == 200
        assert self.org.flags.require_2fa
        self.org_member = self.create_member(user=self.org_user, organization=self.org)
        self.org_index_path = reverse(
            'sentry-organization-home', args=[self.org.slug]
        )
        self.logout_path = reverse(
            'sentry-logout'
        )

        self.sentry_index_path = reverse('sentry')
        self.login_as(self.org_user)

    def test_non_2fa_member_redirected(self):
        import pdb
        pdb.set_trace()
        self.browser.get(self.org_index_path)
        self.browser.wait_until('.circle-indicator')
        # self.browser.wait_until_not('.loading-indicator')
        self.browser.snapshot('organization index  -- 2FA NonCompliant Member')
        assert self.browser.element_exists('.ref-organization-integrations')

    def test_non_2fa_member_can_logout(self):
        self.browser.get(self.logout_path)
        self.browser.wait_until('.org-login')
        self.browser.wait_until_not('.loading-indicator')
        self.browser.snapshot('logout page -- 2FA NonCompliant Member')
        assert self.browser.element_exists('.org-login')

    def test_2fa_member_can_load(self):
        TotpInterface().enroll(self.org_user)
        response = self.client.get(self.org_index_path)
        assert response.status_code == 200
