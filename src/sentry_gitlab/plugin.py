"""
sentry_gitlab.plugin
~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2012 by the Sentry Team, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

from django import forms
from sentry.plugins.bases.issue import IssuePlugin
from django.utils.translation import ugettext_lazy as _
from gitlab import *

import sentry_gitlab



class GitLabOptionsForm(forms.Form):
    gitlab_url = forms.CharField(
        label=_('GitLab URL'),
        widget=forms.TextInput(attrs={'placeholder': 'e.g. https://gitlab.example.com'}),
        help_text=_('Enter the URL for your GitLab server'),
        required=True)

    gitlab_token = forms.CharField(
        label=_('GitLab Private Token'),
        widget=forms.TextInput(attrs={'placeholder': 'e.g. g5DWFtLzaztgYFrqhVfE'}),
        help_text=_('Enter your GitLab API token'),
        required=True)

    gitlab_repo = forms.CharField(
        label=_('Repository Name'),
        widget=forms.TextInput(attrs={'placeholder': 'e.g. namespace/repo'}),
        help_text=_('Enter your repository name, including namespace.'),
        required=True)


class GitLabPlugin(IssuePlugin):
    author = 'Pancentric Ltd'
    author_url = 'https://github.com/pancentric/sentry-gitlab'
    version = sentry_gitlab.VERSION
    description = "Integrate GitLab issues by linking a repository to a project"
    resource_links = [
        ('Bug Tracker', 'https://github.com/pancentric/sentry-gitlab/issues'),
        ('Source', 'https://github.com/pancentric/sentry-gitlab'),
    ]

    slug = 'gitlab'
    title = _('GitLab')
    conf_title = title
    conf_key = 'gitlab'
    project_conf_form = GitLabOptionsForm

    def is_configured(self, request, project, **kwargs):
        return bool(self.get_option('gitlab_repo', project))

    def get_new_issue_title(self, **kwargs):
        return 'Create GitLab Issue'

    def create_issue(self, request, group, form_data, **kwargs):

        url = self.get_option('gitlab_url', group.project)
        token = self.get_option('gitlab_token', group.project)
        repo = self.get_option('gitlab_repo', group.project)
        if repo.find('/') == -1:
            repo_url = str(repo)
        else:
            repo_url = str(repo.replace('/', '%2F'))

        gl = Gitlab(url, token)

        try:
            gl.auth()
        except GitlabAuthenticationError:
            raise forms.ValidationError(_('Unauthorized: Invalid Private Token: %s') % (e,))
        except Exception:
            raise forms.ValidationError(_('Error Communicating with GitLab: %s') % (e,))

        data = {'title': form_data['title'], 'description': form_data['description']}

        proj = gl.Project(id=repo_url)
        issue = proj.Issue(data)
        issue.save()

        return issue.id


    def get_issue_label(self, group, issue_id, **kwargs):
        return 'GL-%s' % issue_id

    def get_issue_url(self, group, issue_id, **kwargs):
        url = self.get_option('gitlab_url', group.project)
        repo = self.get_option('gitlab_repo', group.project)

        return '%s/%s/issues/%s' % (url, repo, issue_id)
