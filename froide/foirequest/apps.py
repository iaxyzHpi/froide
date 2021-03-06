from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class FoiRequestConfig(AppConfig):
    name = 'froide.foirequest'
    verbose_name = _('FOI Request')

    def ready(self):
        from froide.account import account_canceled
        from froide.account.export import registry
        import froide.foirequest.signals  # noqa
        from .utils import cancel_user, export_user_data

        account_canceled.connect(cancel_user)
        registry.register(export_user_data)
