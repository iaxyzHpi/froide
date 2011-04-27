from django import forms
from django.conf import settings
from django.utils.translation import ugettext as _

from publicbody.models import PublicBody
from foirequest.models import FoiRequest, FoiMessage, FoiLaw

new_publicbody_allowed = settings.FROIDE_CONFIG.get(
        'create_new_publicbody', False)
publicbody_empty = settings.FROIDE_CONFIG.get('publicbody_empty', True)
payment_possible = settings.FROIDE_CONFIG.get('payment_possible', False)
payment_possible = settings.FROIDE_CONFIG.get('payment_possible', False)


class RequestForm(forms.Form):
    public_body = forms.CharField(label=_("Public Body"), required=False)
    law = forms.IntegerField(label=_("FOI Law"), widget=forms.HiddenInput,
            required=False)
    subject = forms.CharField(label=_("Subject"),
            widget=forms.TextInput(attrs={'placeholder': _("Subject")}))
    body = forms.CharField(label=_("Body"), 
            widget=forms.Textarea(
            attrs={'placeholder': _("Specify your request here...")}))
    public = forms.BooleanField(required=False, initial=True,
            label=_("This request will be public immediately."))

    def clean_public_body(self):
        pb = self.cleaned_data['public_body']
        if pb == "new":
            if not new_publicbody_allowed:
                raise forms.ValidationError(
                        _("You are not allowed to create a new public body"))
        elif pb == "":
            if not publicbody_empty:
                raise forms.ValidationError(
                        _("You must specify a public body"))
            pb = None
        else:
            try:
                pb_pk = int(pb)
            except ValueError:
                raise forms.ValidationError(_("Invalid value"))
            try:
                public_body = PublicBody.objects.get(pk=pb_pk)
            except PublicBody.DoesNotExist:
                raise forms.ValidationError(_("Invalid value"))
            self.public_body_object = public_body
            self.foi_law_object = public_body.default_law
        return pb
    
    foi_law_object = None

    def clean_law_for_public_body(self, public_body):
        law = self.cleaned_data['law']
        try:
            foi_law = public_body.laws.filter(pk=law).get()
        except FoiLaw.DoesNotExist:
            raise forms.ValidationError(_("Invalid value"))
        self.foi_law_object = foi_law
        return law

    def clean(self):
        cleaned = self.cleaned_data
        public_body = cleaned.get("public_body")
        if public_body is not None and (public_body != "new"
                and public_body != ""):
            self.clean_law_for_public_body(self.public_body_object)
        return cleaned

class SendMessageForm(forms.Form):
    foimessage = forms.IntegerField()

    def clean_foimessage(self):
        foimessage_id = int(self.cleaned_data['foimessage'])
        try:
            self.foimessage_object = FoiMessage.objects.get(pk=foimessage_id)
        except FoiMessage.DoesNotExist:
            raise forms.ValidationError(_("Message not found"))
        return foimessage_id

def get_public_body_suggestions_form_class(queryset):
    if len(queryset):
        class PublicBodySuggestionsForm(forms.Form):
            suggestions = forms.ChoiceField(label=_("Suggestions"),
                    widget=forms.RadioSelect,
                    choices=((s.pk, s.public_body) for s in queryset))

        return PublicBodySuggestionsForm
    return None

def get_status_form_class(foirequest):
    class FoiRequestStatusForm(forms.Form):
        status = forms.ChoiceField(label=_("Status"),
                # widget=forms.RadioSelect,
                choices=(('', '-------'),) + FoiRequest.USER_SET_CHOICES)
        if payment_possible:
            costs = forms.FloatField(label=_("Costs"),
                    required=False, min_value=0.0,
                    localize=True,
                    widget=forms.TextInput(attrs={"size": "4"}))

        refusal_reason = forms.ChoiceField(label=_("Refusal Reason"),
                choices=(('', '-------'),) + 
                foirequest.law.get_refusal_reason_choices(),required=False)

    return FoiRequestStatusForm
