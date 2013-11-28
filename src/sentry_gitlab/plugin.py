"""
sentry_gitlab.plugin
~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2012 by the Sentry Team, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

from django import forms
from django.utils import simplejson
from django.utils.translation import ugettext_lazy as _
from sentry.plugins.bases.issue import IssuePlugin
from gitlab import *

import sentry_gitlab



class GitLabOptionsForm(forms.Form):
    gitlab_url = forms.CharField(label=_('GitLab URL'),
        widget=forms.TextInput(attrs={'placeholder': 'e.g. https://gitlab.example.com'}),
        help_text=_('Enter your GitLab URL here'))

    gitlab_token = forms.CharField(label=_('GitLab Private Token'),
        widget=forms.TextInput(attrs={'placeholder': 'e.g. g5DWFtLzaztgYFrqhVfE'}),
        help_text=_('Enter your GitLab Private Token'))

    gitlab_repo = forms.CharField(label=_('Repository Name'),
        widget=forms.TextInput(attrs={'placeholder': 'e.g. pancentric/repo'}),
        help_text=_('Enter your repository name, including the owner.'))


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
        return bool(self.get_option('repo', project))

    def get_new_issue_title(self, **kwargs):
        return 'Create GitLab Issue'

    def create_issue(self, request, group, form_data, **kwargs):

        url = group.project.gitlab_url
        token = group.project.gitlab_token
        repo_path = group.project.gitlab_repo
        if repo_path.find('/') == -1:
            repo_url = repo_path
        else:
            repo_url = repo_path.replace('/', '%2F')

        gl = Gitlab(url, token)

        try:
            gl.auth()
        except GitlabAuthenticationError:
            raise forms.ValidationError(_('Unauthorized: Invalid Private Token: %s') % (e,))
        except Exception:
            raise forms.ValidationError(_('Error Communicating with GitLab: %s') % (e,))

        data = simplejson.dumps({
            "title": form_data['title'],
            "description": form_data['description']
        })

        proj = gl.Project(id=repo_url)
        issue = proj.Issue(data)
        issue.save()


    def get_issue_label(self, group, issue_id, **kwargs):
        return 'GL-%s' % issue_id

    def get_issue_url(self, group, issue_id, **kwargs):
        url = self.get_option('gitlab_url', group.project)
        repo = self.get_option('gitlab_repo', group.project)

        return '%s/%s/issues/%s' % (url, repo, issue_id)