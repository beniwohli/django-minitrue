from cms.models.titlemodels import Title
from cms.test.util.context_managers import SettingsOverride
from django.contrib.auth.models import User, Permission
from django.core.urlresolvers import reverse
from django.db.models.fields import FieldDoesNotExist
from django.test.testcases import TestCase
from django_load.core import iterload
from migration.api import create_page, create_title
from minitrue.base import Replacer, replacer
from minitrue.models import SearchAndReplace
import sys


class Namespace(object):
    def __getattr__(self, attr):
        ns = Namespace()
        setattr(self, attr, ns)
        return ns


def _reset(replacer):
    modules = []
    for module in iterload('searchreplace'):
        modules.append(module.__name__)
    for module in modules:
        del sys.modules[module]
    replacer._discovered = False
    replacer.models = {}


class ReplacerDiscoverTests(TestCase):
    def test_explicit_register(self):
        """
        Test explicit registration of a model with some configuration
        """
        tmp = Replacer()
        self.assertFalse(tmp._discovered)
        self.assertEqual(len(tmp.models), 0)
        tmp.register(Title, fields=['title', 'redirect'])
        self.assertFalse(tmp._discovered)
        self.assertEqual(len(tmp.models), 1)
        self.assertTrue(Title in tmp.models)
        self.assertEqual(tmp.models[Title].fields, ['title', 'redirect'])
    
    def test_invalid_register(self):
        """
        Test explicit registration of a model with invalid configuration
        """
        tmp = Replacer()
        self.assertFalse(tmp._discovered)
        self.assertEqual(len(tmp.models), 0)
        self.assertRaises(FieldDoesNotExist, tmp.register, SearchAndReplace, fields=['doesnotexist'])
        self.assertFalse(tmp._discovered)
        self.assertEqual(len(tmp.models), 0)
        
    def test_discover(self):
        """
        Test automated (explicit) discovery.
        """
        _reset(replacer) # reset against globally INSTALLED_APPS
        with SettingsOverride(INSTALLED_APPS=['minitrue.testdata']):
            _reset(replacer) # reset against overwritten INSTALLED_APPS
            self.assertFalse(replacer._discovered)
            self.assertEqual(len(replacer.models), 0)
            replacer.discover()
            self.assertTrue(replacer._discovered)
            self.assertEqual(len(replacer.models), 1)
            self.assertTrue(Title in replacer.models)
            self.assertEqual(replacer.models[Title].fields, ['title', 'redirect'])
        
    def test_discover2(self):
        """
        Same as test_discover, tests that those tests don't leak 
        """
        _reset(replacer) # reset against globally INSTALLED_APPS
        with SettingsOverride(INSTALLED_APPS=['minitrue.testdata']):
            _reset(replacer) # reset against overwritten INSTALLED_APPS
            self.assertFalse(replacer._discovered)
            self.assertEqual(len(replacer.models), 0)
            replacer.discover()
            self.assertTrue(replacer._discovered)
            self.assertEqual(len(replacer.models), 1)
            self.assertTrue(Title in replacer.models)
            self.assertEqual(replacer.models[Title].fields, ['title', 'redirect'])
    
    def test_implicit_discover(self):
        """
        Tests implicit discovery when a 'requires_load' decorated method is
        called.
        """
        _reset(replacer) # reset against globally INSTALLED_APPS
        with SettingsOverride(INSTALLED_APPS=['minitrue.testdata']):
            _reset(replacer) # reset against overwritten INSTALLED_APPS
            self.assertFalse(replacer._discovered)
            self.assertEqual(len(replacer.models), 0)
            results = list(replacer.search('test'))
            self.assertTrue(replacer._discovered)
            self.assertEqual(len(replacer.models), 1)
            self.assertEqual(len(results), 1)
            self.assertEqual(len(results[0]), 2)
            info, match_iterator = results[0]
            self.assertEqual(info['object_name'], "Title")
            self.assertEqual(len(list(match_iterator)), 0)
            self.assertTrue(Title in replacer.models)
            self.assertEqual(replacer.models[Title].fields, ['title', 'redirect'])


class SearchReplaceMixin(object):
    def setUp(self):
        """
        All tests are run against different INSTALLED_APPS
        """
        self.data = Namespace() # namespace all test data
        self.data.template = 'testtemplate.html'
        apps = ['minitrue.testdata', 'django.contrib.admin', 'minitrue',
                'project', 'django.contrib.sessions']
        templates = [(self.data.template, 'testtemplate')]
        self.settings_ctx = SettingsOverride(INSTALLED_APPS=apps,
                                             CMS_TEMPLATES=templates)
        self.settings_ctx.__enter__()
        
        self._populate_database()
    
    def tearDown(self):
        self.settings_ctx.__exit__(None, None, None)
        
    def _populate_database(self):
        """
        Create some test content
        """
        self.data.en_title = "English Title"
        self.data.de_title = "Deutscher Titel"
        self.data.redirect = "/title/redirect/"
        page = create_page(self.data.en_title, self.data.template,
                           'en', redirect=self.data.redirect)
        self.data.en_title_instance = page.title_set.get(language='en')
        self.data.de_title_instance = create_title('de', self.data.de_title, page,
                                                   redirect=self.data.redirect)
    
    def _reload(self, obj):
        return obj.__class__.objects.get(pk=obj.pk)


class ReplacerSearchTests(SearchReplaceMixin, TestCase):
    def test_search_case_insensitive_all(self):
        results = list(replacer.search('title'))
        self.assertEqual(len(results), 1)
        # expected results:
        # - English title field
        # - English redirect field
        # - German redirect field
        self.assertEqual(len(results[0][1]), 3)
        matched_instances = [m.instance for m in results[0][1]]
        self.assertTrue(self.data.en_title_instance in matched_instances)
        self.assertTrue(self.data.de_title_instance in matched_instances)
    
    def test_search_case_insensitive_german(self):
        results = list(replacer.search('deutscher'))
        self.assertEqual(len(results), 1)
        self.assertEqual(len(results[0][1]), 1)
        matched_instances = [m.instance for m in results[0][1]]
        self.assertFalse(self.data.en_title_instance in matched_instances)
        self.assertTrue(self.data.de_title_instance in matched_instances)
    
    def test_search_case_sensitive_redirect(self):
        results = list(replacer.search('title', case_sensitive=True))
        self.assertEqual(len(results), 1)
        # expected results:
        # - English redirect field
        # - German redirect field
        self.assertEqual(len(results[0][1]), 2)
        matched_instances = [m.instance for m in results[0][1]]
        self.assertTrue(self.data.en_title_instance in matched_instances)
        self.assertTrue(self.data.de_title_instance in matched_instances)
    
    def test_search_case_sensitive_title(self):
        results = list(replacer.search('Title', case_sensitive=True))
        self.assertEqual(len(results), 1)
        # expected results:
        # - English redirect field
        self.assertEqual(len(results[0][1]), 1)
        matched_instances = [m.instance for m in results[0][1]]
        self.assertTrue(self.data.en_title_instance in matched_instances)
        self.assertFalse(self.data.de_title_instance in matched_instances)


class ReplacerReplaceTests(SearchReplaceMixin, TestCase):
    def setUp(self):
        super(ReplacerReplaceTests, self).setUp()
        self.data.permission = ('add_searchandreplace', 'minitrue', 'searchandreplace')
        
    def _get_admin(self, username, *privileges):
        admin = User()
        admin.username = username
        admin.set_password(username)
        admin.email = '%s@och.ch' % username
        admin.is_staff = True
        admin.is_active = True
        admin.raw_password = username
        admin.save()
        for codename, app_label, model in privileges:
            perm = Permission.objects.get_by_natural_key(codename, app_label, model)
            admin.user_permissions.add(perm)
        return admin
        
    def test_replace_case_insensitive_all(self):
        for queryset in replacer.search_querysets('title', False):
            replacer.replace(queryset, 'title', 'TEST', False)
        de = self._reload(self.data.de_title_instance)
        en = self._reload(self.data.en_title_instance)
        self.assertEqual(de.title, self.data.de_title)
        self.assertEqual(de.redirect, '/TEST/redirect/')
        self.assertEqual(en.title, "English TEST")
        self.assertEqual(en.redirect, '/TEST/redirect/')
    
    def test_replace_admin_no_user(self):
        response = self.client.get(reverse('admin:minitrue_searchandreplace_replace'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/login.html')
        
    def test_overview_admin_no_privileges(self):
        admin = self._get_admin('nopriv')
        self.assertTrue(self.client.login(username=admin.username, password=admin.raw_password))    
        response = self.client.get(reverse('admin:minitrue_searchandreplace_changelist'))
        self.assertEqual(response.status_code, 403)
        self.client.logout()
        
    def test_replace_admin_no_privileges(self):
        admin = self._get_admin('nopriv')
        self.assertTrue(self.client.login(username=admin.username, password=admin.raw_password))    
        response = self.client.get(reverse('admin:minitrue_searchandreplace_replace'))
        self.assertEqual(response.status_code, 403)
        self.client.logout()

    def test_replace_all_admin_no_privileges(self):
        admin = self._get_admin('nopriv')
        self.assertTrue(self.client.login(username=admin.username, password=admin.raw_password))    
        response = self.client.get(reverse('admin:minitrue_searchandreplace_replace_all'))
        self.assertEqual(response.status_code, 403)
        self.client.logout()
        
    def test_overview_admin_with_privileges(self):
        admin = self._get_admin('priv', self.data.permission)
        self.assertTrue(self.client.login(username=admin.username, password=admin.raw_password))    
        response = self.client.get(reverse('admin:minitrue_searchandreplace_changelist'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'minitrue/search_and_replace.html')
        self.client.logout()
        
    def test_admin_replace_get(self):
        admin = self._get_admin('priv', self.data.permission)
        self.assertTrue(self.client.login(username=admin.username, password=admin.raw_password))
        response = self.client.get(reverse('admin:minitrue_searchandreplace_replace'))
        self.assertEqual(response.status_code, 405)
        self.client.logout()
        
    def test_admin_replace_all_get(self):
        admin = self._get_admin('priv', self.data.permission)
        self.assertTrue(self.client.login(username=admin.username, password=admin.raw_password))
        response = self.client.get(reverse('admin:minitrue_searchandreplace_replace_all'))
        self.assertEqual(response.status_code, 405)
        self.client.logout()
    
        
    def test_admin_replace_single(self):
        admin = self._get_admin('priv', self.data.permission)
        self.assertTrue(self.client.login(username=admin.username, password=admin.raw_password))
        data = {
            'app': 'cms',
            'model': 'title',
            'pk': self.data.en_title_instance.pk,
            'field': 'title',
            'term': 'title',
            'replacement': 'TEST',
        }
        response = self.client.post(reverse('admin:minitrue_searchandreplace_replace'), data)
        self.client.logout()
        self.assertEqual(response.status_code, 200, response)
        de = self._reload(self.data.de_title_instance)
        en = self._reload(self.data.en_title_instance)
        self.assertEqual(de.title, self.data.de_title)
        self.assertEqual(de.redirect, '/title/redirect/')
        self.assertEqual(en.title, "English TEST")
        self.assertEqual(en.redirect, '/title/redirect/')
        
    def test_admin_replace_all(self):
        
        admin = self._get_admin('priv', self.data.permission)
        self.assertTrue(self.client.login(username=admin.username, password=admin.raw_password))
        data = {
            'app': 'cms',
            'model': 'title',
            'term': 'title',
            'replacement': 'TEST',
        }
        response = self.client.post(reverse('admin:minitrue_searchandreplace_replace_all'), data)
        self.client.logout()
        self.assertEqual(response.status_code, 200, response)
        de = self._reload(self.data.de_title_instance)
        en = self._reload(self.data.en_title_instance)
        self.assertEqual(de.title, self.data.de_title)
        self.assertEqual(de.redirect, '/TEST/redirect/')
        self.assertEqual(en.title, "English TEST")
        self.assertEqual(en.redirect, '/TEST/redirect/')