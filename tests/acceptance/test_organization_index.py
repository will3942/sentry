from __future__ import absolute_import

from sentry.testutils import AcceptanceTestCase
from django.core.urlresolvers import reverse
from sentry.models import TotpInterface
import six


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
        self.org.flags.require_2fa = True
        self.org.save()

        self.org_member = self.create_member(user=self.org_user, organization=self.org)
        self.org_index_path = reverse(
            'sentry-organization-home', args=[self.org.slug]
        )
        self.logout_path = reverse(
            'sentry-logout'
        )

        self.sentry_index_path = reverse('sentry')
        self.login_as(self.org_user)

    def assert_showing_2fa_page(self):
        assert self.browser.element_exists('.circle-indicator')
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
        def test_orgs(path, num):
            self.browser.get(path)
            self.browser.wait_until_not('.loading-indicator')
            self.browser.snapshot(
                'organization index  -- 2FA NonCompliant Member Multi%s' %
                six.text_type(num))

        org1 = self.create_organization(owner=self.org_user)
        org2 = self.create_organization(owner=self.create_user())
        org3 = self.create_organization(owner=self.create_user())
        org4 = self.create_organization(owner=self.create_user())

        self.create_member(user=self.org_user, organization=org2, role="member")
        self.create_member(user=self.org_user, organization=org3, role="admin")
        self.create_member(user=self.org_user, organization=org4, role="manager")

        org_paths = {
            1: reverse('sentry-organization-home', args=[org1.slug]),
            2: reverse('sentry-organization-home', args=[org2.slug]),
            3: reverse('sentry-organization-home', args=[org3.slug]),
            4: reverse('sentry-organization-home', args=[org4.slug]),
        }

        for num, path in org_paths.items():
            test_orgs(path, num)
            self.assert_showing_org_page()

        test_orgs(self.org_index_path, 0)
        self.assert_showing_2fa_page()
