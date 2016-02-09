import os
import StringIO

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template import Context
from django.template.loader import get_template, render_to_string
from django.utils import timezone
from django.utils.lru_cache import lru_cache
from django.utils.module_loading import import_string
from django.utils.translation import ugettext_lazy as _
from tlt.invoices.models import Job as InvoiceJob
from tlt.invoices.models import Invoice, InvoiceIndex
from wagtail.wagtailadmin.forms import CopyForm
from wagtail.wagtailcore.models import Page
from xhtml2pdf import pisa

from ..models import get_jobindex_content_types

validation = import_string(getattr(settings, 'WAGTAIL_JOBS_VALIDATION', 'wagtailjobs.utils.validation.validation'))
extra_step = import_string(getattr(settings, 'WAGTAIL_JOBS_EXTRA_STEP', 'wagtailjobs.utils.extra_steps.extra_step'))
panel_permissions = import_string(getattr(settings, 'WAGTAIL_JOBS_PANEL_PERMS', 'wagtailjobs.utils.panel_perms.panel_perms'))


@lru_cache(maxsize=None)
def get_job_edit_handler(Job, request):
    return panel_permissions(Job, request)


def send_job(request, job, admin=False):
    # Set Variables
    admin_email_address = settings.ADMIN_EMAIL
    link = request.build_absolute_uri(job.url())
    id = str(job.id)

    def admin_email():
        adminmessage = render_to_string(settings.ADMIN_job_MESSAGE_TEMPLATE_PATH, {
            'job': job,
            'link': link,
            })
        # Email to business owner
        admin_email = EmailMessage(
            'job #' + id,
            adminmessage,
            admin_email_address,
            [admin_email_address])
        admin_email.content_subtype = "html"
        admin_email.send()

    # Customer Email
    def customer_email():
        jobmessage = render_to_string(settings.CLIENT_job_MESSAGE_TEMPLATE_PATH, {
            'job': job,
            'link': link,
        })
        customer_email = EmailMessage('job #' + id, jobmessage, admin_email, [])
        customer_email.content_subtype = "html"
        customer_email.send()
    customer_email()
    if admin is True:
        admin_email()

def serve_pdf(job, request):
    # Convert HTML URIs to absolute system paths so xhtml2pdf can access those resources

    def link_callback(uri, rel):
        # use short variable names
        sUrl = settings.STATIC_URL      # Typically /static/
        sRoot = settings.STATIC_ROOT    # Typically /home/userX/project_static/
        mUrl = settings.MEDIA_URL       # Typically /static/media/
        mRoot = settings.MEDIA_ROOT     # Typically /home/userX/project_static/media/

        # convert URIs to absolute system paths
        if uri.startswith(mUrl):
            path = os.path.join(mRoot, uri.replace(mUrl, ""))
        elif uri.startswith(sUrl):
            path = os.path.join(sRoot, uri.replace(sUrl, ""))

        # make sure that file exists
        if not os.path.isfile(path):
                raise Exception(
                        'media URI must start with %s or %s' % \
                        (sUrl, mUrl))
        return path

    # Render html content through html template with context
    template = get_template('joblist/job_pdf.html')
    html = template.render(Context(job))

    # Write PDF to file
    # file = open(os.path.join(settings.MEDIA_ROOT, 'job #' + str(id) + '.pdf'), "w+b")
    file = StringIO.StringIO()
    pisa.CreatePDF(html, dest=file, link_callback=link_callback)

    # Return PDF document through a Django HTTP response
    file.seek(0)
    # pdf = file.read()
    # file.close()            # Don't forget to close the file handle
    return HttpResponse(file, content_type='application/pdf')


@permission_required('wagtailadmin.access_admin')  # further permissions are enforced within the view
def create(request, pk):
    jobindex = get_object_or_404(Page, pk=pk, content_type__in=get_jobindex_content_types()).specific
    Job = jobindex.get_job_model()
    send_button_name = 'send_job'

    job = Job(jobindex=jobindex)
    EditHandler = get_job_edit_handler(Job, request)
    EditForm = EditHandler.get_form_class(Job)

    if request.method == 'POST':

        form = EditForm(request.POST, request.FILES, instance=job)
        is_sending_job = send_button_name in request.POST
        if form.is_valid() and validation(request, job, is_sending_job):
            extra_step(request, job, form)

            if is_sending_job:
                send_job(request, job)
                messages.success(request, _('The job "{0!s}" has been added').format(job))
                return redirect('wagtailjobs_index', pk=jobindex.pk)

            else:
                messages.success(request, _('The job "{0!s}" has been added').format(job))
                return redirect('wagtailjobs_index', pk=jobindex.pk)
        else:
            messages.error(request, _('The job could not be created due to validation errors'))
            edit_handler = EditHandler(instance=job, form=form)

    else:
        form = EditForm(instance=job)
        edit_handler = EditHandler(instance=job, form=form)

    return render(request, 'wagtailjobs/create.html', {
        'jobindex': jobindex,
        'form': form,
        'send_button_name': send_button_name,
        'edit_handler': edit_handler,
    })


@permission_required('wagtailadmin.access_admin')  # further permissions are enforced within the view
def edit(request, pk, job_pk):
    jobindex = get_object_or_404(Page, pk=pk, content_type__in=get_jobindex_content_types()).specific
    Job = jobindex.get_job_model()
    job = get_object_or_404(Job, jobindex=jobindex, pk=job_pk)
    send_button_name = 'send_job'

    EditHandler = get_job_edit_handler(Job, request)
    EditForm = EditHandler.get_form_class(Job)

    if request.method == 'POST':
        form = EditForm(request.POST, request.FILES, instance=job)

        is_sending_email = send_button_name in request.POST

        if form.is_valid() and validation(request, job, is_sending_email):
            extra_step(request, job, form)

            if is_sending_email:
                send_job(request, job)
                messages.success(request, _('The job "{0!s}" has been updated').format(job))
                return redirect('wagtailjobs_index', pk=jobindex.pk)

            else:
                print job.uuid
                messages.success(request, _('The job "{0!s}" has been updated').format(job))
                return redirect('wagtailjobs_index', pk=jobindex.pk)

        else:
            messages.error(request, _('The job could not be updated due to validation errors'))
            edit_handler = EditHandler(instance=job, form=form)
    else:
        form = EditForm(instance=job)
        edit_handler = EditHandler(instance=job, form=form)

    return render(request, 'wagtailjobs/edit.html', {
        'jobindex': jobindex,
        'job': job,
        'send_button_name': send_button_name,
        'form': form,
        'edit_handler': edit_handler,
    })


@permission_required('wagtailadmin.access_admin')  # further permissions are enforced within the view
def delete(request, pk, job_pk):
    jobindex = get_object_or_404(Page, pk=pk, content_type__in=get_jobindex_content_types()).specific
    Job = jobindex.get_job_model()
    job = get_object_or_404(Job, jobindex=jobindex, pk=job_pk)

    if request.method == 'POST':
        job.delete()
        return redirect('wagtailjobs_index', pk=pk)

    return render(request, 'wagtailjobs/delete.html', {
        'jobindex': jobindex,
        'job': job,
    })


@permission_required('wagtailadmin.access_admin')  # further permissions are enforced within the view
def cancel(request, pk, job_pk):
    jobindex = get_object_or_404(Page, pk=pk, content_type__in=get_jobindex_content_types()).specific
    Job = jobindex.get_job_model()
    job = get_object_or_404(Job, jobindex=jobindex, pk=job_pk)
    if hasattr(job, 'cancelled'):
        if request.method == 'POST':
            job.cancelled = True
            job.save()
            # TODO send email
            return redirect('wagtailjobs_index', pk=pk)

        return render(request, 'wagtailjobs/cancel.html', {
            'jobindex': jobindex,
            'job': job,
        })

@permission_required('wagtailadmin.access_admin')  # further permissions are enforced within the view
def copy(request, pk, job_pk):
    jobindex = get_object_or_404(Page, pk=pk, content_type__in=get_jobindex_content_types()).specific
    Job = jobindex.get_job_model()
    job = Job.objects.get(id=job_pk)

    if request.method == 'POST':
        job.pk = None
        job.uuid = None
        job.issue_date = timezone.now()
        job.save()
        print job.uuid
        print job.pk
        return redirect('wagtailjobs_index', pk=pk)

    return render(request, 'wagtailjobs/copy.html', {
        'jobindex': jobindex,
        'job': job,
    })


@permission_required('wagtailadmin.access_admin')  # further permissions are enforced within the view
def invoice(request, pk, job_pk):
    jobindex = get_object_or_404(Page, pk=pk, content_type__in=get_jobindex_content_types()).specific
    Job = jobindex.get_job_model()
    job = Job.objects.get(id=job_pk)

    if request.method == 'POST':
        invoice = Invoice.objects.create(
            full_name=job.passenger_name,
            invoiceindex=InvoiceIndex.objects.first(),
            phone_number=job.phone_number,
            payment_received=False,
            email=job.passenger_email,
            )
        InvoiceJob.objects.create(
            invoice=invoice,
            job=job
            )
        return redirect('wagtailjobs_index', pk=pk)

    return render(request, 'wagtailjobs/generate_invoice.html', {
        'jobindex': jobindex,
        'job': job,
    })
