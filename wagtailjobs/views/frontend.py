from __future__ import absolute_import, unicode_literals

from uuid import UUID

from django.http import Http404
from django.shortcuts import get_object_or_404


def job_detail(request, jobindex, uuid):
    jobItem = jobindex.get_job_model()
    try:
        uuid = UUID(uuid)
    except ValueError:
        raise Http404
    job = get_object_or_404(jobItem, jobindex=jobindex, uuid=uuid)
    return job.serve(request)


def job_pdf(request, jobindex, uuid):
    jobItem = jobindex.get_job_model()
    try:
        uuid = UUID(uuid)
    except ValueError:
        raise Http404
    job = get_object_or_404(jobItem, jobindex=jobindex, uuid=uuid)
    return job.serve_pdf(request)
