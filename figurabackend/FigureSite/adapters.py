from allauth.account.adapter import DefaultAccountAdapter
from allauth.utils import build_absolute_uri
from django.utils.encoding import force_text

class FigureSiteAccountAdapter(DefaultAccountAdapter):
    def get_email_confirmation_url(self, request, emailconfirmation):
        """Constructs the email confirmation (activation) url.
        Note that if you have architected your system such that email
        confirmations are sent outside of the request context `request`
        can be `None` here.
        """
        url = '/verificar/' + emailconfirmation.key
        ret = build_absolute_uri(
            request,
            url)
        return ret
    
    def format_email_subject(self, subject):
        return force_text(subject)