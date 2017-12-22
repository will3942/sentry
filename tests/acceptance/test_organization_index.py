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
        self.team = self.create_team(organization=self.org, name='Mariachi Band')
        self.create_member(
            user=self.org_owner,
            organization=self.org,
            role='owner',
            teams=[self.team],
        )
        TotpInterface().enroll(self.org_owner)
        self.enable_organization_2fa(self.org)

        self.org_member = self.create_member(user=self.org_user, organization=self.org)
        self.org_index_path = reverse(
            'sentry-organization-home', args=[self.org.slug]
        )
        self.logout_path = reverse(
            'sentry-logout'
        )

        self.sentry_index_path = reverse('sentry')
        self.login_as(self.org_user)

    def enable_organization_2fa(self, organization):
        organization.flags.require_2fa = True
        organization.save()

    def assert_showing_2fa_page(self):
        assert self.browser.element_exists('.twofactor-settings')
        assert reverse('sentry-account-settings-2fa') in self.browser.current_url
        assert not self.browser.element_exists('.organization-home')

    def assert_showing_org_page(self):
        assert not self.browser.element_exists('.circle-indicator')
        assert self.browser.element_exists('.organization-home')

    def test_non_2fa_member_redirected(self):
        self.browser.get(self.org_index_path)
        self.browser.wait_until_not('.loading-indicator')
        self.browser.snapshot('organization index  -- 2FA NonCompliant Member')
        self.assert_showing_2fa_page()

    def test_non_2fa_member_can_logout(self):
        self.browser.get(self.logout_path)
        self.browser.wait_until('.org-login')
        self.browser.wait_until_not('.loading-indicator')
        self.browser.snapshot('logout page -- 2FA NonCompliant Member')
        assert self.browser.element_exists('.org-login')

    def test_2fa_member_can_load(self):
        TotpInterface().enroll(self.org_user)
        self.browser.get(self.org_index_path)
        self.browser.wait_until_not('.loading-indicator')
        self.browser.snapshot('organization index  -- 2FA Compliant Member')
        self.assert_showing_org_page()

    def test_non_2fa_member_multi_org(self):
        def test_orgs(path, label):
            self.browser.get(path)
            self.browser.wait_until_not('.loading-indicator')
            self.browser.snapshot(
                'organization index  -- 2FA NonCompliant Member Multi%s' % label)

        orgs = {
            "Org_Owner": self.create_organization(owner=self.org_user),
            "Org_Member": self.create_organization(owner=self.create_user()),
            "Org_Admin": self.create_organization(owner=self.create_user()),
            "Org_Manager": self.create_organization(owner=self.create_user()),
        }

        self.create_member(user=self.org_user, organization=orgs["Org_Member"], role="member")
        self.create_member(user=self.org_user, organization=orgs["Org_Admin"], role="admin")
        self.create_member(user=self.org_user, organization=orgs["Org_Manager"], role="manager")

        for label, org in orgs.items():
            path = reverse('sentry-organization-home', args=[org.slug])
            test_orgs(path, label)
            self.assert_showing_org_page()

            self.enable_organization_2fa(org)
            test_orgs(path, "Org2FA Enabled " + label)
            self.assert_showing_2fa_page()
