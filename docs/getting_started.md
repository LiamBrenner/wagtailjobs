#Declaring models

Begin by declaring your models something like
``` python
from django.db import models

from wagtail.wagtailadmin.edit_handlers import FieldPanel
from wagtail.wagtailcore.models import Page

from wagtailjobs.models import jobIndexMixin, Abstractjob
from wagtailjobs.decorators import jobindex
from wagtailjobs.utils.payments import get_client_key, do_payment

# The decorator registers this model as a job index
@jobindex
class jobIndex(jobIndexMixin, Page):
    # Add extra fields here, as in a normal Wagtail Page class, if required
    job_model = 'job'


class job(Abstractjob):
    # job is a normal Django model, *not* a Wagtail Page.
    # Add any fields required for your page.
    full_name = models.CharField(max_length=255)
    organization = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=255)
    amount = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        help_text='Without dollar sign($)')
    payment_received = models.BooleanField(default=False)
    

    panels = [
        FieldPanel('full_name', classname='full'),
        FieldPanel('organization'),
        FieldPanel('phone_number')
        FieldPanel('amount'),
        FieldPanel('payment_received'),
    ] + Abstractjob.panels

    def __unicode__(self):
        return self.full_name

    def serve(self, request):
        amount = self.amount
        email = self.email
        # Something like
        if self.payment_received:
            # Bail early and show a thank you for paying message
            return render(request, self.get_template(request), {
                'self': self,
            })
        job_id = self.id
        if request.method == 'POST':
            nonce = request.POST['payment_method_nonce']
            payment_result = do_payment(
                total,
                email,
                nonce,
                job_id)
            if payment_result.is_success:
                # Possibly send a receipt, or get braintree to automatically do it
                self.payment_received = True
                self.save()
                return render(request, self.get_template(request), {
                    'self': self,
                    'result': payment_result,
                })
            else:
                pass
        else:
            payment_result = None

        return render(request, self.get_template(request), {
            "BRAINTREE_CLIENT_KEY": get_client_key(),
            'self': self,
            'result': payment_result,
        })

    preview_modes = [
        ('form', 'Form'),
        ('landing', 'Landing page'),
    ]
```

#Defining settings
Define the following settings where your settings are located 

Add `wagtail.contrib.wagtailroutablepage` to your installed apps and add these settings

``` python
ADMIN_EMAIL = '' # Email for admin to receive job notifactions for paid jobs etc
ADMIN_job_MESSAGE_TEMPLATE_PATH = ''`
PDF_TEMPLATE = '' # Template path for job pdf's relative to the templates folder
CLIENT_job_MESSAGE_TEMPLATE_PATH = '' # Path to job email sent out to clients 
WAGTAIL_jobS_VALIDATION = ''
BRAINTREE_MERCHANT_ID = ''
BRAINTREE_PUBLIC_KEY = ''
BRAINTREE_PRIVATE_KEY = ''
BRAINTREE_CSE_KEY = ''
BRAINTREE_MODE = '' # Production/Sandbox
```


See [Template Rendering](https://wagtailjobs.readthedocs.org/en/latest/template-rendering/#required-templates) and [Custom validation and overriding](https://wagtailjobs.readthedocs.org/en/latest/advanced/#custom-validation-and-overriding) for more information.

There is future scope to have these settings included with [wagtailsettings](https://bitbucket.org/takeflight/wagtailsettings)
