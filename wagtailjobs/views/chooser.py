from django.contrib.auth.decorators import permission_required
from django.shortcuts import redirect, render, get_object_or_404

from wagtail.wagtailcore.models import Page

from ..models import get_jobindex_content_types
from ..forms import SearchForm


@permission_required('wagtailadmin.access_admin')  # further permissions are enforced within the view
def choose(request):
    jobindex_list = Page.objects.filter(content_type__in=get_jobindex_content_types())
    jobindex_count = jobindex_list.count()
    if jobindex_count == 1:
        jobindex = jobindex_list.first()
        return redirect('wagtailjobs_index', pk=jobindex.pk)

    return render(request, 'wagtailjobs/choose.html', {
        'has_job': jobindex_count != 0,
        'jobindex_list': ((jobindex, jobindex.content_type.model_class()._meta.verbose_name)
                           for jobindex in jobindex_list)
    })


@permission_required('wagtailadmin.access_admin')  # further permissions are enforced within the view
def index(request, pk):
    jobindex = get_object_or_404(Page, pk=pk, content_type__in=get_jobindex_content_types()).specific
    job = jobindex.get_job_model()
    job_list = job.objects.filter(jobindex=jobindex)
    form = SearchForm()

    return render(request, 'wagtailjobs/index.html', {
        'jobindex': jobindex,
        'job_list': job_list,
        'form': form,
    })

@permission_required('wagtailadmin.access_admin')  # further permissions are enforced within the view
def search(request, pk):
    jobindex = get_object_or_404(Page, pk=pk, content_type__in=get_jobindex_content_types()).specific
    job = jobindex.get_job_model()
    job_list = job.objects.filter(jobindex=jobindex)
    form = SearchForm(request.GET or None)
    if form.is_valid():
        query = form.cleaned_data['query']
        job_list = job_list.search(query)

    else:
        job_list = job_list.none()

    return render(request, 'wagtailjobs/search.html', {
        'jobindex': jobindex,
        'job_list': job_list,
        'form': form,
    })
